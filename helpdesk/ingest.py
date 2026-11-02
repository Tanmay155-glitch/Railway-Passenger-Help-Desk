"""
Document ingestion module for Railway Passenger Help Desk.
Handles PDF (text + OCR), HTML parsing, and chunking.
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional
import fitz  # PyMuPDF
from bs4 import BeautifulSoup

from helpdesk.config import config
from helpdesk.doc_meta import get_metadata, is_scanned_page
from helpdesk.entities import extract_identifiers

logger = logging.getLogger(__name__)


def ocr_page(image_bytes: bytes, lang: str = "en") -> str:
    """
    Extract text from image using OCR.
    Prefers rapidocr-onnxruntime, falls back to pytesseract.
    
    Args:
        image_bytes: Image data as bytes
        lang: Language code ("en" or "hi")
        
    Returns:
        Extracted text
    """
    # Try rapidocr first
    try:
        from rapidocr_onnxruntime import RapidOCR
        
        engine = RapidOCR()
        result, _ = engine(image_bytes)
        
        if result:
            # Combine all text lines
            text = "\n".join([line[1] for line in result])
            return text
        return ""
        
    except ImportError:
        logger.warning("rapidocr-onnxruntime not available, trying pytesseract")
    
    # Fall back to pytesseract
    try:
        import pytesseract
        from PIL import Image
        import io
        
        image = Image.open(io.BytesIO(image_bytes))
        
        # Set language
        tesseract_lang = "eng" if lang == "en" else "hin"
        text = pytesseract.image_to_string(image, lang=tesseract_lang)
        
        return text
        
    except ImportError:
        logger.error("Neither rapidocr nor pytesseract available for OCR")
        return ""
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""


def ingest_pdf(pdf_path: Path, metadata: dict) -> List[Dict]:
    """
    Extract text from PDF page by page, applying OCR when needed.
    
    Args:
        pdf_path: Path to PDF file
        metadata: Document metadata from doc_meta
        
    Returns:
        List of page dictionaries with text and metadata
    """
    pages = []
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_index = page_num + 1  # 1-indexed for user display
            
            # Try extracting text directly
            text = page.get_text()
            
            needs_ocr = len(text.strip()) < config.MIN_TEXT_CHARS
            
            # Apply OCR if needed or if marked as scanned
            if needs_ocr or is_scanned_page(pdf_path.name, page_index):
                logger.info(f"  OCR: {pdf_path.name} page {page_index}")
                
                # Render page to image at high DPI
                pix = page.get_pixmap(dpi=config.OCR_DPI)
                img_bytes = pix.tobytes("png")
                
                # Determine language
                lang = "hi" if page_index in metadata.get("scanned_pages", []) and "Hindi" in metadata.get("notes", "") else "en"
                
                ocr_text = ocr_page(img_bytes, lang=lang)
                if ocr_text:
                    text = ocr_text
                    needs_ocr = True
            
            pages.append({
                "page_num": page_index,
                "text": text,
                "needs_ocr": needs_ocr,
                "doc": pdf_path.name,
                "issuer": metadata["issuer"],
                "date": metadata["date"],
                "lang": metadata.get("lang", "en")
            })
        
        doc.close()
        
    except Exception as e:
        logger.error(f"Failed to ingest PDF {pdf_path}: {e}")
        raise
    
    return pages


def ingest_html(html_path: Path, metadata: dict) -> List[Dict]:
    """
    Parse HTML and extract text.
    Special handling for 2015 refund table and PIB sections.
    
    Args:
        html_path: Path to HTML file
        metadata: Document metadata from doc_meta
        
    Returns:
        List of chunk dictionaries
    """
    chunks = []
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove scripts, styles, navigation
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        
        # Special handling for 2015 refund rules table
        if "2015" in html_path.name:
            table = soup.find('table')
            if table:
                # Find header row
                headers = [th.get_text(strip=True) for th in table.find_all('th')]
                
                # Process each data row
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        # Create chunk with column headers repeated
                        chunk_text = f"[{html_path.name} | {metadata['issuer']} | {metadata['date']}]\n\n"
                        
                        for i, cell in enumerate(cells):
                            header = headers[i] if i < len(headers) else f"Column {i+1}"
                            value = cell.get_text(strip=True)
                            chunk_text += f"{header}: {value}\n"
                        
                        chunks.append({
                            "text": chunk_text,
                            "doc": html_path.name,
                            "page": None,
                            "issuer": metadata["issuer"],
                            "date": metadata["date"],
                            "lang": metadata.get("lang", "en"),
                            "section": "refund_table"
                        })
        
        # Special handling for PIB document
        elif "pib" in html_path.name.lower():
            # Extract only passenger-relevant sections
            passenger_keywords = ["ticket cancellation", "refund", "boarding point", "passenger"]
            
            # Find all sections
            for section in soup.find_all(['section', 'div', 'article']):
                section_text = section.get_text(strip=True)
                
                # Check if section is passenger-relevant
                is_passenger_section = any(kw in section_text.lower() for kw in passenger_keywords)
                
                if is_passenger_section and len(section_text) > 100:
                    chunk_text = f"[{html_path.name} | {metadata['issuer']} | {metadata['date']}]\n\n"
                    chunk_text += section_text
                    
                    chunks.append({
                        "text": chunk_text,
                        "doc": html_path.name,
                        "page": None,
                        "issuer": metadata["issuer"],
                        "date": metadata["date"],
                        "lang": metadata.get("lang", "en"),
                        "section": "passenger_info"
                    })
        
        # If no special handling matched, extract all text
        if not chunks:
            text = soup.get_text(separator='\n', strip=True)
            chunk_text = f"[{html_path.name} | {metadata['issuer']} | {metadata['date']}]\n\n{text}"
            
            chunks.append({
                "text": chunk_text,
                "doc": html_path.name,
                "page": None,
                "issuer": metadata["issuer"],
                "date": metadata["date"],
                "lang": metadata.get("lang", "en"),
                "section": "full_document"
            })
    
    except Exception as e:
        logger.error(f"Failed to ingest HTML {html_path}: {e}")
        raise
    
    return chunks


def chunk_document(pages: List[Dict], metadata: dict) -> List[Dict]:
    """
    Split document into chunks based on clause structure.
    Target 150-400 words, never split clauses or table rows.
    
    Args:
        pages: List of page dictionaries from ingest_pdf
        metadata: Document metadata
        
    Returns:
        List of chunk dictionaries with full metadata
    """
    chunks = []
    
    # Clause patterns to split on
    clause_patterns = [
        r'^\d+\.',  # "1.", "25."
        r'^\([a-z]\)',  # "(a)", "(b)"
        r'^Rule\s+\d+',  # "Rule 25"
        r'^[A-Z][^:]{0,50}:-',  # "Clerkage Charge:-"
    ]
    
    combined_pattern = '|'.join(f'({p})' for p in clause_patterns)
    
    for page_dict in pages:
        page_text = page_dict["text"]
        page_num = page_dict["page_num"]
        
        # Split into lines
        lines = page_text.split('\n')
        
        current_chunk = []
        current_words = 0
        clause_num = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            words_in_line = len(line.split())
            
            # Check if this line starts a new clause
            is_clause_start = bool(re.match(combined_pattern, line, re.MULTILINE))
            
            # Should we start a new chunk?
            should_split = (
                is_clause_start and 
                current_words >= 150 and  # Minimum chunk size
                current_chunk  # Don't create empty chunks
            )
            
            if should_split:
                # Save current chunk
                chunk_text = '\n'.join(current_chunk)
                clause_num += 1
                
                # Generate chunk ID
                doc_stem = Path(metadata.get("doc", page_dict["doc"])).stem
                chunk_id = f"{doc_stem}_p{page_num:02d}_c{clause_num:02d}"
                
                # Prepend header
                header = f"[{page_dict['doc']} | page {page_num} | {page_dict['issuer']} | {page_dict['date']}]"
                full_text = f"{header}\n\n{chunk_text}"
                
                # Extract identifiers
                identifiers = extract_identifiers(full_text)
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "doc": page_dict["doc"],
                    "page": page_num,
                    "date": page_dict["date"],
                    "issuer": page_dict["issuer"],
                    "doc_type": metadata.get("doc_type", "pdf"),
                    "lang": page_dict.get("lang", "en"),
                    "clause": str(clause_num),
                    "text": full_text,
                    "text_for_embedding": chunk_text,  # Without header
                    "identifiers": identifiers
                })
                
                # Start new chunk with current line
                current_chunk = [line]
                current_words = words_in_line
            else:
                # Add to current chunk
                current_chunk.append(line)
                current_words += words_in_line
            
            # Enforce maximum chunk size
            if current_words > 400 and is_clause_start:
                # Save and restart
                chunk_text = '\n'.join(current_chunk)
                clause_num += 1
                
                doc_stem = Path(metadata.get("doc", page_dict["doc"])).stem
                chunk_id = f"{doc_stem}_p{page_num:02d}_c{clause_num:02d}"
                
                header = f"[{page_dict['doc']} | page {page_num} | {page_dict['issuer']} | {page_dict['date']}]"
                full_text = f"{header}\n\n{chunk_text}"
                
                identifiers = extract_identifiers(full_text)
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "doc": page_dict["doc"],
                    "page": page_num,
                    "date": page_dict["date"],
                    "issuer": page_dict["issuer"],
                    "doc_type": metadata.get("doc_type", "pdf"),
                    "lang": page_dict.get("lang", "en"),
                    "clause": str(clause_num),
                    "text": full_text,
                    "text_for_embedding": chunk_text,
                    "identifiers": identifiers
                })
                
                current_chunk = []
                current_words = 0
        
        # Save remaining chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            clause_num += 1
            
            doc_stem = Path(metadata.get("doc", page_dict["doc"])).stem
            chunk_id = f"{doc_stem}_p{page_num:02d}_c{clause_num:02d}"
            
            header = f"[{page_dict['doc']} | page {page_num} | {page_dict['issuer']} | {page_dict['date']}]"
            full_text = f"{header}\n\n{chunk_text}"
            
            identifiers = extract_identifiers(full_text)
            
            chunks.append({
                "chunk_id": chunk_id,
                "doc": page_dict["doc"],
                "page": page_num,
                "date": page_dict["date"],
                "issuer": page_dict["issuer"],
                "doc_type": metadata.get("doc_type", "pdf"),
                "lang": page_dict.get("lang", "en"),
                "clause": str(clause_num),
                "text": full_text,
                "text_for_embedding": chunk_text,
                "identifiers": identifiers
            })
    
    return chunks
