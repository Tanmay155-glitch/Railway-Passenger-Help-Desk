"""
Unit tests for entity extraction.
Ensures identifiers are correctly extracted from text.
"""

import pytest
from helpdesk.entities import extract_identifiers, has_exact_match


def test_extract_rule_numbers():
    """Test extraction of rule numbers."""
    text = "According to Rule 25 and Rule 30A, passengers must..."
    
    identifiers = extract_identifiers(text)
    
    assert "Rule 25" in identifiers["rules"]
    assert "Rule 30A" in identifiers["rules"]


def test_extract_rule_numbers_case_insensitive():
    """Test that rule extraction is case-insensitive."""
    text = "rule 25 and RULE 30 apply here"
    
    identifiers = extract_identifiers(text)
    
    # Should extract regardless of case
    assert len(identifiers["rules"]) >= 2


def test_extract_circular_numbers():
    """Test extraction of circular numbers."""
    text = "Railway Board circular CC08/2025 and CC10/2024 state..."
    
    identifiers = extract_identifiers(text)
    
    assert any("CC08/2025" in c or "CC 08 / 2025" in c for c in identifiers["circulars"])
    assert any("CC10/2024" in c or "CC 10 / 2024" in c for c in identifiers["circulars"])


def test_extract_circular_with_spaces():
    """Test extraction of circulars with varied spacing."""
    text = "Circular CC 08 / 2025 modifies..."
    
    identifiers = extract_identifiers(text)
    
    assert len(identifiers["circulars"]) > 0


def test_extract_gazette_numbers():
    """Test extraction of gazette notification numbers."""
    text = "Notification G.S.R. 41(E) published on..."
    
    identifiers = extract_identifiers(text)
    
    assert "G.S.R. 41(E)" in identifiers["gazettes"]


def test_extract_train_numbers():
    """Test extraction of 5-digit train numbers."""
    text = "Train 12002 and train 11039-Slip depart from..."
    
    identifiers = extract_identifiers(text)
    
    assert "12002" in identifiers["trains"]
    assert "11039-Slip" in identifiers["trains"]


def test_extract_train_numbers_with_leading_zeros():
    """Test that train numbers preserve leading zeros."""
    text = "Train 01234 is a special train"
    
    identifiers = extract_identifiers(text)
    
    assert "01234" in identifiers["trains"]


def test_extract_rupee_amounts():
    """Test extraction of rupee amounts."""
    text = "The charge is ₹240 or Rs 500 or Rs. 1,000"
    
    identifiers = extract_identifiers(text)
    
    amounts = identifiers["amounts"]
    assert any("240" in a for a in amounts)
    assert any("500" in a for a in amounts)
    assert any("1,000" in a or "1000" in a for a in amounts)


def test_extract_percentage_amounts():
    """Test extraction of percentages."""
    text = "Refund is 75% for cancellation before 48 hours and 50% after"
    
    identifiers = extract_identifiers(text)
    
    assert "75%" in identifiers["amounts"]
    assert "50%" in identifiers["amounts"]


def test_extract_empty_text():
    """Test extraction from empty text."""
    identifiers = extract_identifiers("")
    
    assert identifiers["rules"] == []
    assert identifiers["circulars"] == []
    assert identifiers["gazettes"] == []
    assert identifiers["trains"] == []
    assert identifiers["amounts"] == []


def test_extract_no_identifiers():
    """Test extraction when text has no identifiers."""
    text = "This is just regular text with no special identifiers."
    
    identifiers = extract_identifiers(text)
    
    # All should be empty lists
    assert all(len(v) == 0 for v in identifiers.values())


def test_extract_multiple_of_same_type():
    """Test extraction of multiple identifiers of the same type."""
    text = "Rule 1, Rule 2, Rule 3, Rule 25, and Rule 30 all apply"
    
    identifiers = extract_identifiers(text)
    
    # Should extract all unique rule numbers
    assert len(identifiers["rules"]) >= 5


def test_has_exact_match_with_match():
    """Test has_exact_match returns True when there's a match."""
    query_ids = {
        "rules": ["Rule 25"],
        "circulars": [],
        "gazettes": [],
        "trains": [],
        "amounts": []
    }
    
    chunk_ids = {
        "rules": ["Rule 25", "Rule 30"],
        "circulars": ["CC08/2025"],
        "gazettes": [],
        "trains": [],
        "amounts": []
    }
    
    assert has_exact_match(query_ids, chunk_ids) == True


def test_has_exact_match_without_match():
    """Test has_exact_match returns False when there's no match."""
    query_ids = {
        "rules": ["Rule 25"],
        "circulars": [],
        "gazettes": [],
        "trains": [],
        "amounts": []
    }
    
    chunk_ids = {
        "rules": ["Rule 30"],
        "circulars": ["CC08/2025"],
        "gazettes": [],
        "trains": [],
        "amounts": []
    }
    
    assert has_exact_match(query_ids, chunk_ids) == False


def test_has_exact_match_case_insensitive():
    """Test that has_exact_match is case-insensitive."""
    query_ids = {
        "rules": ["RULE 25"],
        "circulars": [],
        "gazettes": [],
        "trains": [],
        "amounts": []
    }
    
    chunk_ids = {
        "rules": ["rule 25"],
        "circulars": [],
        "gazettes": [],
        "trains": [],
        "amounts": []
    }
    
    assert has_exact_match(query_ids, chunk_ids) == True


def test_has_exact_match_multiple_categories():
    """Test has_exact_match with matches in multiple categories."""
    query_ids = {
        "rules": ["Rule 25"],
        "circulars": [],
        "gazettes": [],
        "trains": ["12002"],
        "amounts": []
    }
    
    chunk_ids = {
        "rules": ["Rule 30"],
        "circulars": [],
        "gazettes": [],
        "trains": ["12002", "11039"],
        "amounts": []
    }
    
    # Should match on trains
    assert has_exact_match(query_ids, chunk_ids) == True


def test_extract_identifiers_deduplicates():
    """Test that extract_identifiers removes duplicates."""
    text = "Rule 25 and Rule 25 and Rule 25 apply"
    
    identifiers = extract_identifiers(text)
    
    # Should only have one instance
    assert identifiers["rules"].count("Rule 25") == 1


def test_extract_slip_trains():
    """Test extraction of slip train numbers."""
    text = "Train 11039-Slip is a special coach"
    
    identifiers = extract_identifiers(text)
    
    assert "11039-Slip" in identifiers["trains"]


def test_extract_returns_dict_with_all_keys():
    """Test that extract_identifiers always returns dict with all expected keys."""
    text = "Any text"
    
    identifiers = extract_identifiers(text)
    
    assert "rules" in identifiers
    assert "circulars" in identifiers
    assert "gazettes" in identifiers
    assert "trains" in identifiers
    assert "amounts" in identifiers
    assert all(isinstance(v, list) for v in identifiers.values())
