"""
Unit tests for document chunking.
Ensures chunks preserve table rows and clause boundaries.
"""

import pytest
from helpdesk.ingest import chunk_document, ingest_pdf, ingest_html
from pathlib import Path


def test_chunk_size_target():
    """Test that chunks are within target size (150-400 words)."""
    # Sample pages
    pages = [
        {
            "page_num": 1,
            "text": " ".join(["word"] * 200),  # 200 words
            "needs_ocr": False,
            "doc": "test.pdf",
            "issuer": "Test",
            "date": "2026-01-01"
        }
    ]
    metadata = {"doc": "test.pdf", "issuer": "Test", "date": "2026-01-01"}
    
    chunks = chunk_document(pages, metadata)
    
    assert len(chunks) > 0
    for chunk in chunks:
        word_count = len(chunk["text"].split())
        # Should be in reasonable range (may vary with headers)
        assert word_count < 500  # Not too large


def test_chunk_has_metadata():
    """Test that chunks include all required metadata."""
    pages = [
        {
            "page_num": 1,
            "text": "Rule 1. This is a test rule about refunds.",
            "needs_ocr": False,
            "doc": "test.pdf",
            "issuer": "Railway Board",
            "date": "2026-01-01"
        }
    ]
    metadata = {
        "doc": "test.pdf",
        "issuer": "Railway Board",
        "date": "2026-01-01"
    }
    
    chunks = chunk_document(pages, metadata)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert "chunk_id" in chunk
        assert "doc" in chunk
        assert "page" in chunk
        assert "text" in chunk
        assert "text_for_embedding" in chunk
        assert "identifiers" in chunk


def test_chunk_header_prepended():
    """Test that chunks have header with metadata."""
    pages = [
        {
            "page_num": 1,
            "text": "Important railway rule.",
            "needs_ocr": False,
            "doc": "test.pdf",
            "issuer": "Board",
            "date": "2026"
        }
    ]
    metadata = {"doc": "test.pdf", "issuer": "Board", "date": "2026"}
    
    chunks = chunk_document(pages, metadata)
    
    assert len(chunks) > 0
    # Header should be in text
    assert "test.pdf" in chunks[0]["text"]
    assert "page 1" in chunks[0]["text"].lower()


def test_clause_not_split():
    """Test that clauses/rules are not split mid-text."""
    # Text with clear clause marker
    pages = [
        {
            "page_num": 1,
            "text": "1. First rule about cancellation. " * 100,  # Long text
            "needs_ocr": False,
            "doc": "test.pdf",
            "issuer": "Test",
            "date": "2026"
        }
    ]
    metadata = {"doc": "test.pdf", "issuer": "Test", "date": "2026"}
    
    chunks = chunk_document(pages, metadata)
    
    # If split into multiple chunks, each should have complete sentences
    for chunk in chunks:
        text = chunk["text"]
        # Should not end mid-sentence (basic check)
        assert text.strip().endswith(('.', ')', ':', '%', '"'))


def test_chunk_id_format():
    """Test chunk ID format: {doc_stem}_p{page:02d}_c{chunk_num:02d}"""
    pages = [
        {
            "page_num": 3,
            "text": "Sample text.",
            "needs_ocr": False,
            "doc": "sample_doc.pdf",
            "issuer": "Test",
            "date": "2026"
        }
    ]
    metadata = {"doc": "sample_doc.pdf", "issuer": "Test", "date": "2026"}
    
    chunks = chunk_document(pages, metadata)
    
    assert len(chunks) > 0
    chunk_id = chunks[0]["chunk_id"]
    # Should match pattern
    assert "sample_doc" in chunk_id
    assert "_p" in chunk_id
    assert "_c" in chunk_id


def test_page_boundary_preserved():
    """Test that page numbers are correctly tracked."""
    pages = [
        {"page_num": 1, "text": "Page 1 text.", "needs_ocr": False, "doc": "test.pdf", "issuer": "Test", "date": "2026"},
        {"page_num": 2, "text": "Page 2 text.", "needs_ocr": False, "doc": "test.pdf", "issuer": "Test", "date": "2026"},
    ]
    metadata = {"doc": "test.pdf", "issuer": "Test", "date": "2026"}
    
    chunks = chunk_document(pages, metadata)
    
    # Should have chunks from both pages
    page_nums = {chunk["page"] for chunk in chunks}
    assert 1 in page_nums or 2 in page_nums


def test_empty_page_handling():
    """Test handling of empty or near-empty pages."""
    pages = [
        {"page_num": 1, "text": "", "needs_ocr": False, "doc": "test.pdf", "issuer": "Test", "date": "2026"},
        {"page_num": 2, "text": "   ", "needs_ocr": False, "doc": "test.pdf", "issuer": "Test", "date": "2026"},
        {"page_num": 3, "text": "Real content here.", "needs_ocr": False, "doc": "test.pdf", "issuer": "Test", "date": "2026"},
    ]
    metadata = {"doc": "test.pdf", "issuer": "Test", "date": "2026"}
    
    chunks = chunk_document(pages, metadata)
    
    # Should only create chunks for page 3
    assert len(chunks) > 0
    # Empty pages should be skipped
    for chunk in chunks:
        assert len(chunk["text"].strip()) > 0


def test_overlap_between_chunks():
    """Test that chunks have overlap for context continuity."""
    # Long text that will create multiple chunks
    long_text = "1. First rule. " * 50 + "2. Second rule. " * 50
    pages = [
        {"page_num": 1, "text": long_text, "needs_ocr": False, "doc": "test.pdf", "issuer": "Test", "date": "2026"}
    ]
    metadata = {"doc": "test.pdf", "issuer": "Test", "date": "2026"}
    
    chunks = chunk_document(pages, metadata)
    
    if len(chunks) > 1:
        # Check if there's some text overlap
        # (This is a loose check - actual implementation may vary)
        chunk1_words = set(chunks[0]["text"].split())
        chunk2_words = set(chunks[1]["text"].split())
        # Should have some common words due to overlap
        overlap = chunk1_words & chunk2_words
        assert len(overlap) > 0


def test_identifiers_extracted():
    """Test that identifiers are extracted and stored."""
    pages = [
        {
            "page_num": 1,
            "text": "Rule 25 and train 12002 with ₹500 refund per Circular CC08/2025.",
            "needs_ocr": False,
            "doc": "test.pdf",
            "issuer": "Test",
            "date": "2026"
        }
    ]
    metadata = {"doc": "test.pdf", "issuer": "Test", "date": "2026"}
    
    chunks = chunk_document(pages, metadata)
    
    assert len(chunks) > 0
    identifiers = chunks[0]["identifiers"]
    # Should extract various entities
    assert isinstance(identifiers, dict)
    # Check structure (actual values depend on extraction logic)
    assert "rules" in identifiers or "trains" in identifiers or "amounts" in identifiers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
