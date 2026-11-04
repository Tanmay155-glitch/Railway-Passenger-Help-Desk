"""
Unit tests for source citation builder.
Ensures source citations are accurate and properly formatted.
"""

import pytest
from helpdesk.answer import build_sources


def test_build_sources_basic():
    """Test basic source citation building."""
    chunk_ids = ["doc1_p01_c01", "doc1_p02_c01", "doc2_p01_c01"]
    all_chunks = [
        {
            "chunk_id": "doc1_p01_c01",
            "doc": "irctc_refund_rules_jan2026.pdf",
            "page": 1,
            "text": "Sample text"
        },
        {
            "chunk_id": "doc1_p02_c01",
            "doc": "irctc_refund_rules_jan2026.pdf",
            "page": 2,
            "text": "Sample text"
        },
        {
            "chunk_id": "doc2_p01_c01",
            "doc": "rb_cc08_2025_tatkal.pdf",
            "page": 1,
            "text": "Sample text"
        },
    ]
    
    sources = build_sources(chunk_ids, all_chunks)
    
    assert len(sources) > 0
    assert len(sources) <= 4  # Should limit to 2-4 sources
    
    # Check structure
    for source in sources:
        assert "doc" in source
        assert "page" in source
        assert isinstance(source["doc"], str)
        assert isinstance(source["page"], (int, type(None)))


def test_deduplication():
    """Test that duplicate doc+page combinations are removed."""
    chunk_ids = ["doc1_p01_c01", "doc1_p01_c02", "doc1_p01_c03"]
    all_chunks = [
        {
            "chunk_id": "doc1_p01_c01",
            "doc": "test.pdf",
            "page": 1,
            "text": "Text"
        },
        {
            "chunk_id": "doc1_p01_c02",
            "doc": "test.pdf",
            "page": 1,
            "text": "More text"
        },
        {
            "chunk_id": "doc1_p01_c03",
            "doc": "test.pdf",
            "page": 1,
            "text": "Even more text"
        },
    ]
    
    sources = build_sources(chunk_ids, all_chunks)
    
    # Should only have one source (same doc + page)
    assert len(sources) == 1
    assert sources[0]["doc"] == "test.pdf"
    assert sources[0]["page"] == 1


def test_relevance_ordering():
    """Test that sources are ordered by relevance (chunk_id order)."""
    chunk_ids = ["doc3_p01_c01", "doc1_p01_c01", "doc2_p01_c01"]
    all_chunks = [
        {"chunk_id": "doc1_p01_c01", "doc": "doc1.pdf", "page": 1, "text": ""},
        {"chunk_id": "doc2_p01_c01", "doc": "doc2.pdf", "page": 1, "text": ""},
        {"chunk_id": "doc3_p01_c01", "doc": "doc3.pdf", "page": 1, "text": ""},
    ]
    
    sources = build_sources(chunk_ids, all_chunks)
    
    # First source should be from doc3 (first in chunk_ids)
    assert sources[0]["doc"] == "doc3.pdf"


def test_html_page_null():
    """Test that HTML documents have page: null."""
    chunk_ids = ["html_p00_c01"]
    all_chunks = [
        {
            "chunk_id": "html_p00_c01",
            "doc": "indianrail_refund_rules_2015.html",
            "page": None,
            "text": "HTML content"
        }
    ]
    
    sources = build_sources(chunk_ids, all_chunks)
    
    assert len(sources) == 1
    assert sources[0]["page"] is None


def test_source_limit():
    """Test that sources are limited to 2-4 entries."""
    # Create 10 chunks from different pages
    chunk_ids = [f"doc_p{i:02d}_c01" for i in range(1, 11)]
    all_chunks = [
        {
            "chunk_id": f"doc_p{i:02d}_c01",
            "doc": "test.pdf",
            "page": i,
            "text": f"Page {i}"
        }
        for i in range(1, 11)
    ]
    
    sources = build_sources(chunk_ids, all_chunks)
    
    # Should be limited
    assert len(sources) >= 2
    assert len(sources) <= 4


def test_empty_chunk_ids():
    """Test handling of empty chunk_ids list."""
    sources = build_sources([], [])
    
    assert sources == []


def test_missing_chunk():
    """Test handling when chunk_id not found in all_chunks."""
    chunk_ids = ["missing_chunk"]
    all_chunks = [
        {"chunk_id": "exists", "doc": "test.pdf", "page": 1, "text": ""}
    ]
    
    # Should not crash
    sources = build_sources(chunk_ids, all_chunks)
    
    # May return empty or skip missing chunks
    assert isinstance(sources, list)


def test_mixed_pdf_and_html():
    """Test mixed PDF and HTML sources."""
    chunk_ids = ["pdf_p01_c01", "html_p00_c01"]
    all_chunks = [
        {
            "chunk_id": "pdf_p01_c01",
            "doc": "rules.pdf",
            "page": 1,
            "text": "PDF text"
        },
        {
            "chunk_id": "html_p00_c01",
            "doc": "rules.html",
            "page": None,
            "text": "HTML text"
        },
    ]
    
    sources = build_sources(chunk_ids, all_chunks)
    
    assert len(sources) == 2
    # PDF should have page number
    pdf_source = next(s for s in sources if s["doc"] == "rules.pdf")
    assert pdf_source["page"] == 1
    # HTML should have null page
    html_source = next(s for s in sources if s["doc"] == "rules.html")
    assert html_source["page"] is None


def test_multiple_pages_same_doc():
    """Test multiple pages from same document."""
    chunk_ids = ["doc_p01_c01", "doc_p03_c01", "doc_p05_c01"]
    all_chunks = [
        {"chunk_id": "doc_p01_c01", "doc": "test.pdf", "page": 1, "text": ""},
        {"chunk_id": "doc_p03_c01", "doc": "test.pdf", "page": 3, "text": ""},
        {"chunk_id": "doc_p05_c01", "doc": "test.pdf", "page": 5, "text": ""},
    ]
    
    sources = build_sources(chunk_ids, all_chunks)
    
    # Should have 3 sources (different pages)
    assert len(sources) == 3
    pages = [s["page"] for s in sources]
    assert 1 in pages
    assert 3 in pages
    assert 5 in pages


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
