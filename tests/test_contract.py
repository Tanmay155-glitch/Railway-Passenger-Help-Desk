"""
Test the output contract for ask() function.
"""

import pytest
from helpdesk.pipeline import ask


def test_ask_returns_dict():
    """Test that ask() always returns a dictionary."""
    result = ask("test question")
    assert isinstance(result, dict)


def test_ask_has_required_keys():
    """Test that ask() output has all required keys."""
    result = ask("test question")
    
    required_keys = {"answer", "sources", "sql", "dont_know"}
    assert set(result.keys()) == required_keys


def test_ask_answer_is_string():
    """Test that answer is a string."""
    result = ask("test question")
    assert isinstance(result["answer"], str)


def test_ask_sources_is_list():
    """Test that sources is a list."""
    result = ask("test question")
    assert isinstance(result["sources"], list)


def test_ask_sql_is_string_or_none():
    """Test that sql is a string or None."""
    result = ask("test question")
    assert result["sql"] is None or isinstance(result["sql"], str)


def test_ask_dont_know_is_bool():
    """Test that dont_know is a boolean."""
    result = ask("test question")
    assert isinstance(result["dont_know"], bool)


def test_ask_never_raises():
    """Test that ask() never raises exceptions."""
    # Try various invalid inputs
    test_cases = [
        "",
        None,
        "a" * 10000,  # Very long
        "🚂🚃🚃",  # Unicode
        "DROP TABLE users;",  # SQL injection attempt
    ]
    
    for question in test_cases:
        try:
            result = ask(str(question))
            assert isinstance(result, dict)
            assert "dont_know" in result
        except Exception as e:
            pytest.fail(f"ask() raised exception for input '{question}': {e}")


def test_source_structure():
    """Test that source items have correct structure."""
    result = ask("test question")
    
    for source in result["sources"]:
        assert isinstance(source, dict)
        assert "doc" in source
        assert "page" in source
        assert isinstance(source["doc"], str)
        assert source["page"] is None or isinstance(source["page"], int)
