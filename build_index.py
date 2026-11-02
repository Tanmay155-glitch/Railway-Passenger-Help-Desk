"""
Build index script for Railway Passenger Help Desk.
Ingests documents, applies OCR, generates embeddings, and builds search indexes.
"""

import json
import logging
import time
from pathlib import Path
from typing import List, Dict
import sys

from helpdesk.config import config, find_data_pack, find_document, validate_environment
from helpdesk.doc_meta import DOC_METADATA, list_documents
from helpdesk.ingest import ingest_pdf, ingest_html, chunk_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main build process:
    1. Validate environment
    2. Discover and ingest documents
    3. Generate embeddings
    4. Build BM25 index
    5. Extract database schema
    6. Save to index/
    """
    logger.info("=" * 60)
    logger.info("Railway Passenger Help Desk - Index Builder")
    logger.info("=" * 60)
    
    # Validate environment
    is_valid, errors = validate_environment()
    if not is_valid:
        logger.error("Environment validation failed:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    logger.info("✓ Environment validated")
    
    # Check for database
    db_path = find_data_pack()
    if not db_path:
        logger.error("Database not found. Unzip rail_capstone_pack.zip into data/")
        sys.exit(1)
    
    logger.info(f"✓ Found database: {db_path}")
    
    # Process all documents
    all_chunks = []
    doc_stats = []
    
    logger.info(f"\nProcessing {len(list_documents())} documents...")
    
    for doc_name in list_documents():
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {doc_name}")
        logger.info(f"{'='*60}")
        
        # Find document
        doc_path = find_document(doc_name)
        if not doc_path:
            logger.warning(f"  Document not found: {doc_name}")
            continue
        
        # Get metadata
        metadata = DOC_METADATA[doc_name]
        metadata["doc"] = doc_name  # Add filename to metadata
        
        try:
            # Ingest based on file type
            if doc_name.endswith('.pdf'):
                pages = ingest_pdf(doc_path, metadata)
                chunks = chunk_document(pages, metadata)
                
                # Count OCR pages
                ocr_pages = [p["page_num"] for p in pages if p["needs_ocr"]]
                
                doc_stats.append({
                    "doc": doc_name,
                    "pages": len(pages),
                    "ocr_pages": len(ocr_pages),
                    "ocr_page_nums": ocr_pages,
                    "chunks": len(chunks)
                })
                
            elif doc_name.endswith('.html'):
                chunks = ingest_html(doc_path, metadata)
                
                doc_stats.append({
                    "doc": doc_name,
                    "pages": "N/A (HTML)",
                    "ocr_pages": 0,
                    "ocr_page_nums": [],
                    "chunks": len(chunks)
                })
            
            else:
                logger.warning(f"  Unknown file type: {doc_name}")
                continue
            
            logger.info(f"  ✓ Created {len(chunks)} chunks")
            all_chunks.extend(chunks)
            
        except Exception as e:
            logger.error(f"  ✗ Failed to process {doc_name}: {e}", exc_info=True)
            continue
    
    # Save chunks
    logger.info(f"\n{'='*60}")
    logger.info(f"Saving {len(all_chunks)} chunks to index/chunks.json...")
    
    config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    chunks_file = config.INDEX_DIR / "chunks.json"
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    logger.info(f"  ✓ Saved to {chunks_file}")
    
    # Extract database schema
    logger.info("\nExtracting database schema...")
    try:
        import sqlite3
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table schemas
        cursor.execute("SELECT sql FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'")
        schema_lines = []
        
        for row in cursor.fetchall():
            if row[0]:
                schema_lines.append(row[0])
        
        schema_text = "\n\n".join(schema_lines)
        
        # Add helpful notes
        schema_text += "\n\n-- Notes:\n"
        schema_text += "-- * stops view: SELECT * FROM schedules WHERE is_halt = 1\n"
        schema_text += "-- * Use stops for 'trains from A to B' questions\n"
        schema_text += "-- * train.number is TEXT (keeps leading zeros)\n"
        schema_text += "-- * Overnight: travel_min = (day_b - day_a) * 1440 + minutes(arrival_b) - minutes(departure_a)\n"
        
        schema_file = config.INDEX_DIR / "schema.txt"
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(schema_text)
        
        conn.close()
        
        logger.info(f"  ✓ Saved schema to {schema_file}")
        
    except Exception as e:
        logger.error(f"  ✗ Failed to extract schema: {e}")
    
    # Generate embeddings
    logger.info(f"\n{'='*60}")
    logger.info("Generating embeddings...")
    logger.info(f"{'='*60}")
    
    try:
        from fastembed import TextEmbedding
        import numpy as np
        
        # Initialize embedding model
        model = TextEmbedding("BAAI/bge-small-en-v1.5")
        logger.info("Loaded embedding model: BAAI/bge-small-en-v1.5")
        
        # Extract texts for embedding
        texts = [chunk.get('text_for_embedding', chunk.get('text', '')) for chunk in all_chunks]
        
        # Generate embeddings
        logger.info(f"Embedding {len(texts)} chunks...")
        embeddings_list = list(model.embed(texts))
        embeddings = np.array(embeddings_list)
        
        # Save embeddings
        emb_file = config.INDEX_DIR / "embeddings.npy"
        np.save(emb_file, embeddings)
        
        logger.info(f"  ✓ Saved embeddings: {embeddings.shape} to {emb_file}")
        
    except ImportError:
        logger.warning("  ✗ fastembed not available, skipping embeddings")
        logger.warning("  Install with: pip install fastembed")
    except Exception as e:
        logger.warning(f"  ✗ Embedding generation failed: {e}")
    
    # Build BM25 index
    logger.info(f"\n{'='*60}")
    logger.info("Building BM25 index...")
    logger.info(f"{'='*60}")
    
    try:
        from rank_bm25 import BM25Okapi
        import pickle
        
        # Tokenize texts
        corpus = []
        for chunk in all_chunks:
            text = chunk.get('text_for_embedding', chunk.get('text', ''))
            tokens = text.lower().split()
            corpus.append(tokens)
        
        # Build BM25
        bm25 = BM25Okapi(corpus)
        
        # Save BM25
        bm25_file = config.INDEX_DIR / "bm25.pkl"
        with open(bm25_file, 'wb') as f:
            pickle.dump(bm25, f)
        
        logger.info(f"  ✓ Saved BM25 index to {bm25_file}")
        
    except ImportError:
        logger.warning("  ✗ rank_bm25 not available, skipping BM25")
        logger.warning("  Install with: pip install rank-bm25")
    except Exception as e:
        logger.warning(f"  ✗ BM25 build failed: {e}")
    
    # Save manifest
    manifest = {
        "build_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_chunks": len(all_chunks),
        "total_documents": len(doc_stats),
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "bm25_model": "BM25Okapi"
    }
    
    manifest_file = config.INDEX_DIR / "manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    logger.info(f"  ✓ Saved manifest to {manifest_file}")
    
    # Print summary table
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"{'Document':<50} {'Pages':<10} {'OCR':<10} {'Chunks':<10}")
    logger.info(f"{'-'*50} {'-'*10} {'-'*10} {'-'*10}")
    
    for stat in doc_stats:
        pages_str = str(stat['pages']) if isinstance(stat['pages'], int) else stat['pages']
        ocr_str = f"{stat['ocr_pages']} pages" if stat['ocr_pages'] > 0 else "-"
        
        logger.info(f"{stat['doc']:<50} {pages_str:<10} {ocr_str:<10} {stat['chunks']:<10}")
    
    logger.info(f"\nTotal chunks: {len(all_chunks)}")
    logger.info(f"\n✓ Index build complete!")
    logger.info(f"✓ Files saved to {config.INDEX_DIR}/")
    logger.info(f"\nNext steps:")
    logger.info(f"  1. Implement search.py (hybrid retrieval)")
    logger.info(f"  2. Implement sql.py (text-to-SQL)")
    logger.info(f"  3. Implement answer.py (grounded generation)")
    logger.info(f"  4. Complete pipeline.py routing")
    logger.info(f"  5. Test with: python ask.py 'What is the refund for Tatkal?'")


if __name__ == "__main__":
    main()
