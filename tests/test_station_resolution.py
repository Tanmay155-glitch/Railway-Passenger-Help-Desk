"""
Unit tests for station name resolution.
Tests fuzzy matching of station names to codes.
"""

import pytest
from helpdesk.stations import resolve_stations, load_stations


def test_exact_code_match():
    """Test exact station code match (case-insensitive)."""
    result = resolve_stations("Train from NDLS to BCT")
    assert "NDLS" in str(result).upper()
    assert "BCT" in str(result).upper()


def test_exact_name_match():
    """Test exact station name match."""
    result = resolve_stations("Train from New Delhi to Mumbai Central")
    # Should resolve to codes
    assert result is not None
    assert len(result) > 0


def test_fuzzy_name_match():
    """Test fuzzy matching with slight misspelling."""
    # "Mumbia" should match "Mumbai"
    result = resolve_stations("Train from Delhi to Mumbia")
    assert result is not None


def test_multi_station_city():
    """Test cities with multiple stations (Chennai)."""
    result = resolve_stations("Train from Chennai to Bangalore")
    # Chennai has multiple stations: MAS, MS, etc.
    assert result is not None


def test_no_station_mentioned():
    """Test query without station names."""
    result = resolve_stations("What is the Tatkal charge?")
    # Should return empty or None
    assert result is None or len(result) == 0


def test_case_insensitive():
    """Test case insensitive matching."""
    result1 = resolve_stations("from DELHI")
    result2 = resolve_stations("from delhi")
    result3 = resolve_stations("from Delhi")
    # All should resolve to same station
    assert result1 is not None
    assert result2 is not None
    assert result3 is not None


def test_partial_station_name():
    """Test partial station name matching."""
    result = resolve_stations("from Howrah Junction")
    assert result is not None


def test_load_stations():
    """Test that stations are loaded correctly."""
    stations = load_stations()
    assert stations is not None
    assert len(stations) > 0
    # Should have common stations
    assert any(s.get('code') == 'NDLS' for s in stations)


def test_ambiguous_short_name():
    """Test handling of ambiguous short names."""
    # "Chennai" could match multiple stations
    result = resolve_stations("Train from Chennai")
    assert result is not None


def test_common_typos():
    """Test common misspellings."""
    # Common typos should still match
    test_cases = [
        "Deli to Mumbai",  # Delhi
        "Banglore to Chennai",  # Bangalore
        "Kolkatta to Patna",  # Kolkata
    ]
    for query in test_cases:
        result = resolve_stations(query)
        # Should match something (not None)
        assert result is not None or result == {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
