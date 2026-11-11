"""
Search module for Railway Passenger Help Desk.
Implements hybrid retrieval: BM25 + dense embeddings + exact-match boosting.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import List, Dict, Optional
import numpy as np

from helpdesk.config import config
from helpdesk.entities import extract_identifiers, has_exact_match

logger = logging.getLogger(__name__)

# Global cache for loaded indexes
_chunks = None
_bm25 = None
_embeddings = None
_embedding_model = None


def load_chunks() -> List[Dict]:
    """Load chunks from index."""
    global _chunks
    
    if _chunks is not None:
        return _chunks
    
    chunks_file = config.INDEX_DIR / "chunks.json"
    if not chunks_file.exists():
        logger.error(f"Chunks file not found: {chunks_file}. Run build_index.py first.")
        return []
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        _chunks = json.load(f)
    
    logger.info(f"Loaded {len(_chunks)} chunks from index")
    return _chunks


def load_bm25():
    """Load BM25 index from pickle."""
    global _bm25
    
    if _bm25 is not None:
        return _bm25
    
    bm25_file = config.INDEX_DIR / "bm25.pkl"
    if not bm25_file.exists():
        logger.warning(f"BM25 index not found: {bm25_file}")
        return None
    
    with open(bm25_file, 'rb') as f:
        _bm25 = pickle.load(f)
    
    logger.info("Loaded BM25 index")
    return _bm25


def load_embeddings() -> Optional[np.ndarray]:
    """Load embeddings from numpy file."""
    global _embeddings
    
    if _embeddings is not None:
        return _embeddings
    
    emb_file = config.INDEX_DIR / "embeddings.npy"
    if not emb_file.exists():
        logger.warning(f"Embeddings file not found: {emb_file}")
        return None
    
    _embeddings = np.load(emb_file)
    logger.info(f"Loaded embeddings: {_embeddings.shape}")
    return _embeddings


def get_embedding_model():
    """Get or initialize embedding model."""
    global _embedding_model
    
    if _embedding_model is not None:
        return _embedding_model
    
    try:
        from fastembed import TextEmbedding
        _embedding_model = TextEmbedding("BAAI/bge-small-en-v1.5")
        logger.info("Loaded fastembed model")
        return _embedding_model
    except ImportError:
        logger.warning("fastembed not available")
        return None
    except Exception as e:
        logger.warning(f"Failed to load embedding model: {e}")
        return None


def search_bm25(question: str, k: int = 20) -> List[Dict]:
    """
    Search using BM25 keyword matching.
    
    Args:
        question: Query text
        k: Number of results to return
        
    Returns:
        List of chunks with scores
    """
    chunks = load_chunks()
    if not chunks:
        return []
    
    bm25 = load_bm25()
    if bm25 is None:
        logger.warning("BM25 not available, returning empty results")
        return []
    
    # Tokenize query
    query_tokens = question.lower().split()
    
    # Get scores
    scores = bm25.get_scores(query_tokens)
    
    # Get top-k indices
    top_indices = np.argsort(scores)[::-1][:k]
    
    results = []
    for idx in top_indices:
        chunk = chunks[idx].copy()
        chunk['score'] = float(scores[idx])
        chunk['search_type'] = 'bm25'
        results.append(chunk)
    
    return results


def search_dense(question: str, k: int = 20) -> List[Dict]:
    """
    Search using dense embeddings with cosine similarity.
    
    Args:
        question: Query text
        k: Number of results to return
        
    Returns:
        List of chunks with scores
    """
    chunks = load_chunks()
    if not chunks:
        return []
    
    embeddings = load_embeddings()
    if embeddings is None:
        logger.warning("Embeddings not available")
        return []
    
    # Get embedding model
    model = get_embedding_model()
    if model is None:
        logger.warning("Embedding model not available")
        return []
    
    try:
        # Embed query
        query_embedding = list(model.embed([question]))[0]
        query_embedding = np.array(query_embedding)
        
        # Compute cosine similarity
        # Normalize vectors
        query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
        doc_norms = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10)
        
        # Dot product
        scores = np.dot(doc_norms, query_norm)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:k]
        
        results = []
        for idx in top_indices:
            chunk = chunks[idx].copy()
            chunk['score'] = float(scores[idx])
            chunk['search_type'] = 'dense'
            results.append(chunk)
        
        return results
        
    except Exception as e:
        logger.error(f"Dense search failed: {e}")
        return []


def reciprocal_rank_fusion(
    bm25_results: List[Dict],
    dense_results: List[Dict],
    k: int = 60
) -> List[Dict]:
    """
    Merge BM25 and dense results using Reciprocal Rank Fusion.
    
    Args:
        bm25_results: Results from BM25 search
        dense_results: Results from dense search
        k: RRF constant (default 60)
        
    Returns:
        Merged and sorted results
    """
    # Build rank maps
    chunk_scores = {}
    
    # Add BM25 ranks
    for rank, result in enumerate(bm25_results):
        chunk_id = result.get('chunk_id', result.get('text', '')[:50])
        rrf_score = 1.0 / (k + rank + 1)
        chunk_scores[chunk_id] = {
            'chunk': result,
            'rrf_score': rrf_score,
            'bm25_rank': rank + 1
        }
    
    # Add dense ranks
    for rank, result in enumerate(dense_results):
        chunk_id = result.get('chunk_id', result.get('text', '')[:50])
        rrf_score = 1.0 / (k + rank + 1)
        
        if chunk_id in chunk_scores:
            chunk_scores[chunk_id]['rrf_score'] += rrf_score
            chunk_scores[chunk_id]['dense_rank'] = rank + 1
        else:
            chunk_scores[chunk_id] = {
                'chunk': result,
                'rrf_score': rrf_score,
                'dense_rank': rank + 1
            }
    
    # Sort by RRF score
    merged = sorted(
        chunk_scores.values(),
        key=lambda x: x['rrf_score'],
        reverse=True
    )
    
    # Extract chunks with updated scores
    results = []
    for item in merged:
        chunk = item['chunk'].copy()
        chunk['score'] = item['rrf_score']
        chunk['search_type'] = 'rrf'
        if 'bm25_rank' in item:
            chunk['bm25_rank'] = item['bm25_rank']
        if 'dense_rank' in item:
            chunk['dense_rank'] = item['dense_rank']
        results.append(chunk)
    
    return results


def boost_exact_matches(
    results: List[Dict],
    question: str,
    boost: float = None
) -> List[Dict]:
    """
    Boost chunks that have exact identifier matches with the question.
    
    Args:
        results: Search results
        question: Query text
        boost: Boost multiplier (default from config)
        
    Returns:
        Results with boosted scores
    """
    if boost is None:
        boost = config.EXACT_MATCH_BOOST
    
    # Extract identifiers from question
    question_ids = extract_identifiers(question)
    
    boosted = []
    for chunk in results:
        chunk = chunk.copy()
        
        # Get chunk identifiers
        chunk_ids = chunk.get('identifiers', {})
        
        # Check for exact match
        if has_exact_match(question_ids, chunk_ids):
            chunk['score'] *= boost
            chunk['exact_match'] = True
            logger.debug(f"Boosted chunk {chunk.get('chunk_id', '?')} for exact match")
        else:
            chunk['exact_match'] = False
        
        boosted.append(chunk)
    
    # Re-sort by boosted scores
    boosted.sort(key=lambda x: x['score'], reverse=True)
    
    return boosted


def get_neighboring_chunks(chunk_ids: List[str], chunks: List[Dict] = None) -> List[Dict]:
    """
    Get neighboring chunks (previous and next) for context.
    
    Args:
        chunk_ids: List of chunk IDs
        chunks: All chunks (loaded if not provided)
        
    Returns:
        List of neighboring chunks
    """
    if chunks is None:
        chunks = load_chunks()
    
    # Build a map of chunk_id to index
    chunk_map = {chunk.get('chunk_id', ''): i for i, chunk in enumerate(chunks)}
    
    neighbors = []
    seen = set()
    
    for chunk_id in chunk_ids:
        if chunk_id not in chunk_map:
            continue
        
        idx = chunk_map[chunk_id]
        
        # Add previous chunk (same document)
        if idx > 0:
            prev_chunk = chunks[idx - 1]
            if prev_chunk.get('doc') == chunks[idx].get('doc'):
                prev_id = prev_chunk.get('chunk_id', '')
                if prev_id and prev_id not in seen:
                    neighbors.append(prev_chunk)
                    seen.add(prev_id)
        
        # Add next chunk (same document)
        if idx < len(chunks) - 1:
            next_chunk = chunks[idx + 1]
            if next_chunk.get('doc') == chunks[idx].get('doc'):
                next_id = next_chunk.get('chunk_id', '')
                if next_id and next_id not in seen:
                    neighbors.append(next_chunk)
                    seen.add(next_id)
    
    return neighbors


def apply_date_awareness(results: List[Dict]) -> List[Dict]:
    """
    When chunks from different documents address the same topic,
    include all with their dates for precedence evaluation.
    
    Args:
        results: Search results
        
    Returns:
        Results with date precedence metadata
    """
    # Group by topic (same identifiers or similar keywords)
    topic_groups = {}
    
    for chunk in results:
        # Simple grouping by main identifiers
        ids = chunk.get('identifiers', {})
        
        # Create a topic key
        topic_key = tuple(sorted(
            ids.get('rules', []) + 
            ids.get('circulars', []) + 
            ids.get('trains', [])
        ))
        
        if not topic_key:
            # No clear topic, use as is
            topic_key = ('misc', chunk.get('chunk_id', ''))
        
        if topic_key not in topic_groups:
            topic_groups[topic_key] = []
        
        topic_groups[topic_key].append(chunk)
    
    # For each topic with multiple documents, mark precedence
    enhanced = []
    for topic_key, group in topic_groups.items():
        if len(group) > 1:
            # Check if different documents
            docs = set(c.get('doc', '') for c in group)
            if len(docs) > 1:
                # Sort by date (newer first)
                group.sort(key=lambda x: x.get('date', ''), reverse=True)
                
                # Mark precedence
                for i, chunk in enumerate(group):
                    chunk = chunk.copy()
                    chunk['precedence'] = i + 1  # 1 = newest, 2 = older, etc.
                    if i == 0:
                        chunk['is_latest'] = True
                    enhanced.append(chunk)
            else:
                enhanced.extend(group)
        else:
            enhanced.extend(group)
    
    return enhanced


def search(question: str, k: int = None, include_neighbors: bool = True) -> tuple[List[Dict], List[Dict]]:
    """
    Main search function using hybrid retrieval.
    
    Combines BM25 keyword search, dense embeddings, RRF fusion,
    exact-match boosting, and date awareness.
    
    Args:
        question: Query text
        k: Number of results to return (default from config)
        include_neighbors: Whether to return neighboring chunks for context
        
    Returns:
        Tuple of (main_results, neighbor_chunks) where:
        - main_results: List of top-k chunks with scores and metadata
        - neighbor_chunks: List of neighboring chunks for context (empty if include_neighbors=False)
    """
    if k is None:
        k = config.RETRIEVAL_K
    
    logger.info(f"Searching for: {question[:50]}...")
    
    # BM25 search
    bm25_results = search_bm25(question, k=20)
    logger.debug(f"BM25 found {len(bm25_results)} results")
    
    # Dense search (with fallback)
    dense_results = search_dense(question, k=20)
    logger.debug(f"Dense search found {len(dense_results)} results")
    
    # If dense search failed, use BM25 only
    if not dense_results:
        logger.warning("Dense search unavailable, using BM25 only")
        results = bm25_results[:k]
    else:
        # Merge with RRF
        results = reciprocal_rank_fusion(bm25_results, dense_results)
        logger.debug(f"RRF merged to {len(results)} results")
    
    # Boost exact matches
    results = boost_exact_matches(results, question)
    
    # Apply date awareness
    results = apply_date_awareness(results)
    
    # Take top-k
    results = results[:k]
    
    # Add neighboring chunks for context
    neighbors = []
    if include_neighbors:
        main_chunk_ids = [r.get('chunk_id', '') for r in results if r.get('chunk_id')]
        neighbors = get_neighboring_chunks(main_chunk_ids)
        
        # Mark results as having neighbors
        for result in results:
            result['has_neighbors'] = len(neighbors) > 0
    
    logger.info(f"Returning {len(results)} results (+ {len(neighbors)} neighbors)")
    
    return results, neighbors


def search_with_context(question: str, k: int = None) -> tuple[List[Dict], List[Dict]]:
    """
    Search and return both main results and neighboring chunks.
    
    Args:
        question: Query text
        k: Number of main results
        
    Returns:
        Tuple of (main_results, neighbor_chunks)
    """
    return search(question, k)
