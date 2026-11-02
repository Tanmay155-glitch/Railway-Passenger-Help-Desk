"""
Document metadata catalog for Railway Passenger Help Desk.
Contains metadata for all documents in the data pack.
Only metadata is stored here - no answers or document content.
"""

from typing import Dict, List, Optional
from datetime import date


DOC_METADATA: Dict[str, dict] = {
    "indianrail_refund_rules_2015.html": {
        "issuer": "Indian Railways",
        "date": "2015-11-12",
        "doc_type": "html",
        "scanned_pages": [],
        "lang": "en",
        "notes": "Table with Pre revised and Revised columns. Keep each row with both column labels."
    },
    "irctc_refund_rules_jan2026.pdf": {
        "issuer": "IRCTC",
        "date": "2026-01-19",
        "doc_type": "pdf_text",
        "scanned_pages": [],
        "lang": "en",
        "tdr_table_pages": [8, 9, 10],
        "notes": "Numbered clauses 1 to 16 and TDR table spanning pages 8-10"
    },
    "rb_cc10_2024_advance_reservation.pdf": {
        "issuer": "Railway Board",
        "date": "2024-10-16",
        "doc_type": "pdf_scanned",
        "scanned_pages": [1, 2],
        "lang": "en",
        "notes": "p1 English, p2 Hindi. No text layer"
    },
    "rb_cc08_2025_tatkal.pdf": {
        "issuer": "Railway Board",
        "date": "2025-06-10",
        "doc_type": "pdf_mixed",
        "scanned_pages": [3, 4, 5, 6],
        "lang": "en",
        "notes": "p1-2 English with text, p3-6 Hindi scanned"
    },
    "rb_cc10_2025_reservation_charts.pdf": {
        "issuer": "Railway Board",
        "date": "2025-07-02",
        "doc_type": "pdf_scanned",
        "scanned_pages": [1, 2],
        "lang": "mixed",
        "notes": "p1 Hindi, p2 English. No text layer"
    },
    "rb_cc08_2026_vande_bharat_sleeper_refund.pdf": {
        "issuer": "Railway Board",
        "date": "2026-01-19",
        "doc_type": "pdf_text",
        "scanned_pages": [],
        "lang": "mixed",
        "notes": "p1-2 circular, p3-4 gazette in Hindi, p5 gazette in English. Gazette G.S.R. 41(E) of 16 Jan 2026"
    },
    "pib_2026-03-24_reform_express.html": {
        "issuer": "PIB Delhi",
        "date": "2026-03-24",
        "doc_type": "html",
        "scanned_pages": [],
        "lang": "en",
        "notes": "Only 'Ticket cancellation and refund' and 'Change of Train Boarding Point' sections matter to passengers"
    }
}


def get_metadata(filename: str) -> Optional[dict]:
    """
    Get metadata for a document by filename.
    
    Args:
        filename: Name of the document file
        
    Returns:
        Metadata dictionary or None if not found
    """
    return DOC_METADATA.get(filename)


def list_documents() -> List[str]:
    """
    Get list of all document filenames in the catalog.
    
    Returns:
        List of document filenames
    """
    return list(DOC_METADATA.keys())


def is_scanned_page(filename: str, page_num: int) -> bool:
    """
    Check if a specific page is scanned (requires OCR).
    
    Args:
        filename: Document filename
        page_num: Page number (1-indexed)
        
    Returns:
        True if page is scanned, False otherwise
    """
    meta = get_metadata(filename)
    if not meta:
        return False
    
    return page_num in meta.get("scanned_pages", [])
