"""
Test entity extraction from text.
"""

import pytest
from helpdesk.entities import extract_identifiers, has_exact_match


def test_extract_rule_numbers():
    """Test extraction of rule numbers."""
    text = "According to Rule 25 and Rule 26A, refunds are processed."
    ids = extract_identifiers(text)
    
    assert "Rule 25" in ids["rules"]
    assert "Rule 26A" in ids["rules"]


def test_extract_circular_numbers():
    """Test extraction of circular numbers."""
    text = "As per Circular CC08/2025 and CC 10 / 2024, new rules apply."
    ids = extract_identifiers(text)
    
    assert len(ids["circulars"]) >= 2
    assert any("CC08" in c or "08" in c for c in ids["circulars"])


def test_extract_gazette_numbers():
    """Test extraction of gazette numbers."""
    text = "Gazette notification G.S.R. 41(E) dated 16 Jan 2026."
    ids = extract_identifiers(text)
    
    assert "G.S.R. 41(E)" in ids["gazettes"]


def test_extract_train_numbers():
    """Test extraction of train numbers."""
    text = "Train 12002 and 11039-Slip will depart at 10:00."
    ids = extract_identifiers(text)
    
    assert "12002" in ids["trains"]
    assert "11039-Slip" in ids["trains"]


def test_extract_amounts():
    """Test extraction of amounts."""
    text = "Refund is ₹240 or 30% of fare, whichever is less. Also Rs 150 is charged."
    ids = extract_identifiers(text)
    
    assert any("240" in a for a in ids["amounts"])
    assert "30%" in ids["amounts"]


def test_no_false_positives():
    """Test that ordinary text doesn't generate false positives."""
    text = "This is a simple sentence with no special identifiers."
    ids = extract_identifiers(text)
    
    assert len(ids["rules"]) == 0
    assert len(ids["circulars"]) == 0
    assert len(ids["gazettes"]) == 0
    assert len(ids["trains"]) == 0


def test_has_exact_match_positive():
    """Test exact match detection - positive case."""
    query_ids = extract_identifiers("What is Rule 25?")
    chunk_ids = extract_identifiers("Rule 25 states that refunds are...")
    
    assert has_exact_match(query_ids, chunk_ids)


def test_has_exact_match_negative():
    """Test exact match detection - negative case."""
    query_ids = extract_identifiers("What is Rule 25?")
    chunk_ids = extract_identifiers("Rule 26 states something else.")
    
    assert not has_exact_match(query_ids, chunk_ids)


def test_case_insensitive_matching():
    """Test that matching is case-insensitive."""
    query_ids = extract_identifiers("What is RULE 25?")
    chunk_ids = extract_identifiers("rule 25 states that...")
    
    assert has_exact_match(query_ids, chunk_ids)
