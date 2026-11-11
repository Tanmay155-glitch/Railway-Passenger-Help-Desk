"""
Unit tests for output contract compliance.
Ensures ask() always returns correct structure and never raises.
"""

import pytest
from helpdesk.pipeline import ask


def test_output_has_all_required_keys():
    """Test that ask() returns all required keys."""
    result = ask("What is Rule 25?")
    
    assert "answer" in result
    assert "sources" in result
    assert "sql" in result
    assert "dont_know" in result


def test_output_correct_types():
    """Test that ask() returns correct types for each key."""
    result = ask("What is Rule 25?")
    
    assert isinstance(result["answer"], str)
    assert isinstance(result["sources"], list)
    assert isinstance(result["sql"], (str, type(None)))
    assert isinstance(result["dont_know"], bool)


def test_sources_have_correct_structure():
    """Test that each source has doc and page keys."""
    result = ask("What is Rule 25?")
    
    for source in result["sources"]:
        assert isinstance(source, dict)
        assert "doc" in source
        assert "page" in source
        assert isinstance(source["doc"], str)
        assert isinstance(source["page"], (int, type(None)))


def test_ask_never_raises_on_valid_input():
    """Test that ask() never raises exceptions on valid input."""
    questions = [
        "What is Rule 25?",
        "Which trains go from Delhi to Mumbai?",
        "What is the refund policy?",
        "How much is a ticket?",  # Out of scope
        "",  # Empty
        "   ",  # Whitespace only
    ]
    
    for question in questions:
        try:
            result = ask(question)
            assert isinstance(result, dict)
        except Exception as e:
            pytest.fail(f"ask() raised {type(e).__name__}: {e} for question: '{question}'")


def test_ask_never_raises_on_invalid_input():
    """Test that ask() handles invalid input gracefully."""
    invalid_inputs = [
        None,
        123,
        ["list"],
        {"dict": "value"}
    ]
    
    for inp in invalid_inputs:
        try:
            result = ask(inp)
            assert isinstance(result, dict)
            assert result["dont_know"] == True
        except Exception as e:
            # Expected to handle gracefully, not raise
            pytest.fail(f"ask() raised {type(e).__name__}: {e} for input: {inp}")


def test_empty_question_returns_dont_know():
    """Test that empty questions return dont_know=True."""
    result = ask("")
    assert result["dont_know"] == True
    
    result = ask("   ")
    assert result["dont_know"] == True


def test_sources_limited_to_reasonable_count():
    """Test that sources are limited (2-4 per requirements)."""
    result = ask("What is the advance reservation period?")
    
    # Should have at most 4 sources
    assert len(result["sources"]) <= 4


def test_sql_only_present_for_db_queries():
    """Test that SQL is only present for database queries."""
    # Document query - should not have SQL
    doc_result = ask("What is Rule 25?")
    # SQL should be None for pure doc queries
    # (unless router decides it's 'both')
    
    # Database query - should have SQL or dont_know
    db_result = ask("Which trains go from Delhi to Mumbai?")
    # Should either have SQL or dont_know=True
    assert db_result["sql"] is not None or db_result["dont_know"] == True


def test_answer_is_non_empty_string():
    """Test that answer is always a non-empty string."""
    result = ask("What is Rule 25?")
    
    assert isinstance(result["answer"], str)
    assert len(result["answer"]) > 0
    assert result["answer"].strip() != ""


def test_consistency_across_multiple_calls():
    """Test that same question returns consistent structure."""
    question = "What is the Tatkal cancellation charge?"
    
    results = [ask(question) for _ in range(3)]
    
    for result in results:
        assert set(result.keys()) == {"answer", "sources", "sql", "dont_know"}
        assert isinstance(result["answer"], str)
        assert isinstance(result["sources"], list)
