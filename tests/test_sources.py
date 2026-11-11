"""
Unit tests for source citation building.
Ensures sources are correctly extracted from chunks.
"""

import pytest
from helpdesk.answer import build_sources


def test_build_sources_extracts_doc_and_page():
    """Test that build_sources extracts doc and page from chunks."""
    chunks = [
        {
            "chunk_id": "doc1_p01_c01",
            "doc": "test_doc.pdf",
            "page": 1
        },
        {
            "chunk_id": "doc1_p02_c01",
            "doc": "test_doc.pdf",
            "page": 2
        }
    ]
    
    chunk_ids = ["doc1_p01_c01", "doc1_p02_c01"]
    
    sources = build_sources(chunk_ids, chunks)
    
    assert len(sources) == 2
    assert sources[0]["doc"] == "test_doc.pdf"
    assert sources[0]["page"] == 1
    assert sources[1]["doc"] == "test_doc.pdf"
    assert sources[1]["page"] == 2


def test_build_sources_deduplicates():
    """Test that build_sources removes duplicate doc+page combinations."""
    chunks = [
        {
            "chunk_id": "doc1_p01_c01",
            "doc": "test_doc.pdf",
            "page": 1
        },
        {
            "chunk_id": "doc1_p01_c02",
            "doc": "test_doc.pdf",
            "page": 1  # Same page as previous
        },
        {
            "chunk_id": "doc1_p02_c01",
            "doc": "test_doc.pdf",
            "page": 2
        }
    ]
    
    chunk_ids = ["doc1_p01_c01", "doc1_p01_c02", "doc1_p02_c01"]
    
    sources = build_sources(chunk_ids, chunks)
    
    # Should deduplicate page 1
    assert len(sources) == 2
    assert sources[0]["page"] == 1
    assert sources[1]["page"] == 2


def test_build_sources_limits_to_four():
    """Test that build_sources limits results to 2-4 sources."""
    chunks = [
        {"chunk_id": f"doc_p{i:02d}_c01", "doc": f"doc{i}.pdf", "page": i}
        for i in range(1, 11)  # 10 different pages
    ]
    
    chunk_ids = [f"doc_p{i:02d}_c01" for i in range(1, 11)]
    
    sources = build_sources(chunk_ids, chunks)
    
    # Should limit to at most 4
    assert len(sources) <= 4


def test_build_sources_handles_null_page():
    """Test that build_sources handles HTML documents with page=None."""
    chunks = [
        {
            "chunk_id": "html_doc_c01",
            "doc": "document.html",
            "page": None
        }
    ]
    
    chunk_ids = ["html_doc_c01"]
    
    sources = build_sources(chunk_ids, chunks)
    
    assert len(sources) == 1
    assert sources[0]["doc"] == "document.html"
    assert sources[0]["page"] is None


def test_build_sources_preserves_order():
    """Test that build_sources maintains order from chunk_ids (relevance order)."""
    chunks = [
        {"chunk_id": "doc_p03_c01", "doc": "doc.pdf", "page": 3},
        {"chunk_id": "doc_p01_c01", "doc": "doc.pdf", "page": 1},
        {"chunk_id": "doc_p02_c01", "doc": "doc.pdf", "page": 2}
    ]
    
    # Order: page 3, then page 1, then page 2
    chunk_ids = ["doc_p03_c01", "doc_p01_c01", "doc_p02_c01"]
    
    sources = build_sources(chunk_ids, chunks)
    
    # Should maintain the order from chunk_ids
    assert sources[0]["page"] == 3
    assert sources[1]["page"] == 1
    assert sources[2]["page"] == 2


def test_build_sources_handles_missing_chunk_ids():
    """Test that build_sources handles chunk IDs not in chunks list."""
    chunks = [
        {"chunk_id": "doc_p01_c01", "doc": "doc.pdf", "page": 1}
    ]
    
    chunk_ids = ["doc_p01_c01", "missing_chunk_id", "doc_p02_c01"]
    
    sources = build_sources(chunk_ids, chunks)
    
    # Should only return source for valid chunk_id
    assert len(sources) == 1
    assert sources[0]["page"] == 1


def test_build_sources_handles_empty_chunk_ids():
    """Test that build_sources handles empty chunk_ids list."""
    chunks = [
        {"chunk_id": "doc_p01_c01", "doc": "doc.pdf", "page": 1}
    ]
    
    sources = build_sources([], chunks)
    
    assert len(sources) == 0


def test_build_sources_structure():
    """Test that each source has exactly doc and page keys."""
    chunks = [
        {
            "chunk_id": "doc_p01_c01",
            "doc": "test.pdf",
            "page": 1,
            "date": "2026-01-01",
            "issuer": "Test",
            "extra_field": "should not be in source"
        }
    ]
    
    chunk_ids = ["doc_p01_c01"]
    
    sources = build_sources(chunk_ids, chunks)
    
    assert len(sources) == 1
    source = sources[0]
    
    # Should have exactly doc and page
    assert "doc" in source
    assert "page" in source
    # Should not have extra fields
    assert "date" not in source
    assert "issuer" not in source
    assert "extra_field" not in source


def test_build_sources_multiple_docs():
    """Test that build_sources handles multiple different documents."""
    chunks = [
        {"chunk_id": "doc1_p01_c01", "doc": "doc1.pdf", "page": 1},
        {"chunk_id": "doc2_p05_c01", "doc": "doc2.pdf", "page": 5},
        {"chunk_id": "doc3_c01", "doc": "doc3.html", "page": None}
    ]
    
    chunk_ids = ["doc1_p01_c01", "doc2_p05_c01", "doc3_c01"]
    
    sources = build_sources(chunk_ids, chunks)
    
    assert len(sources) == 3
    
    # Check each document is represented
    docs = [s["doc"] for s in sources]
    assert "doc1.pdf" in docs
    assert "doc2.pdf" in docs
    assert "doc3.html" in docs
