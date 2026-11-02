"""
Test SQL safety guards.
"""

import pytest
from helpdesk.sql_guard import guard_sql, strip_comments, wrap_with_limit


def test_guard_allows_select():
    """Test that SELECT queries are allowed."""
    sql = "SELECT * FROM trains WHERE number = '12002'"
    is_safe, reason = guard_sql(sql)
    assert is_safe is True
    assert reason == ""


def test_guard_allows_with():
    """Test that WITH queries are allowed."""
    sql = "WITH x AS (SELECT * FROM trains) SELECT * FROM x"
    is_safe, reason = guard_sql(sql)
    assert is_safe is True


def test_guard_rejects_insert():
    """Test that INSERT is rejected."""
    sql = "INSERT INTO trains VALUES ('12345', 'Test')"
    is_safe, reason = guard_sql(sql)
    assert is_safe is False
    assert "INSERT" in reason


def test_guard_rejects_update():
    """Test that UPDATE is rejected."""
    sql = "UPDATE trains SET name = 'Hacked' WHERE number = '12002'"
    is_safe, reason = guard_sql(sql)
    assert is_safe is False
    assert "UPDATE" in reason


def test_guard_rejects_delete():
    """Test that DELETE is rejected."""
    sql = "DELETE FROM trains WHERE number = '12002'"
    is_safe, reason = guard_sql(sql)
    assert is_safe is False
    assert "DELETE" in reason


def test_guard_rejects_drop():
    """Test that DROP is rejected."""
    sql = "DROP TABLE trains"
    is_safe, reason = guard_sql(sql)
    assert is_safe is False
    assert "DROP" in reason


def test_guard_rejects_alter():
    """Test that ALTER is rejected."""
    sql = "ALTER TABLE trains ADD COLUMN test TEXT"
    is_safe, reason = guard_sql(sql)
    assert is_safe is False
    assert "ALTER" in reason


def test_guard_rejects_pragma():
    """Test that PRAGMA is rejected."""
    sql = "PRAGMA query_only = OFF"
    is_safe, reason = guard_sql(sql)
    assert is_safe is False
    assert "PRAGMA" in reason


def test_guard_rejects_multiple_statements():
    """Test that multiple statements are rejected."""
    sql = "SELECT * FROM trains; DROP TABLE stations;"
    is_safe, reason = guard_sql(sql)
    assert is_safe is False
    assert "Multiple statements" in reason


def test_guard_strips_comments():
    """Test that comments are stripped."""
    sql = "SELECT * FROM trains -- this is a comment"
    is_safe, reason = guard_sql(sql)
    assert is_safe is True  # Should pass after stripping comment


def test_strip_comments_single_line():
    """Test stripping single-line comments."""
    sql = "SELECT * FROM trains -- comment"
    result = strip_comments(sql)
    assert "--" not in result
    assert "SELECT" in result


def test_strip_comments_multi_line():
    """Test stripping multi-line comments."""
    sql = "SELECT /* comment */ * FROM trains"
    result = strip_comments(sql)
    assert "/*" not in result
    assert "*/" not in result
    assert "SELECT" in result


def test_wrap_with_limit_no_existing():
    """Test wrapping SQL without existing LIMIT."""
    sql = "SELECT * FROM trains"
    wrapped = wrap_with_limit(sql, limit=50)
    assert "LIMIT 50" in wrapped


def test_wrap_with_limit_existing_smaller():
    """Test that smaller existing LIMIT is kept."""
    sql = "SELECT * FROM trains LIMIT 10"
    wrapped = wrap_with_limit(sql, limit=50)
    assert "LIMIT 10" in wrapped
    assert "LIMIT 50" not in wrapped


def test_wrap_with_limit_existing_larger():
    """Test that larger existing LIMIT is replaced."""
    sql = "SELECT * FROM trains LIMIT 100"
    wrapped = wrap_with_limit(sql, limit=50)
    assert "LIMIT 50" in wrapped


def test_guard_rejects_empty():
    """Test that empty SQL is rejected."""
    is_safe, reason = guard_sql("")
    assert is_safe is False
    assert "Empty" in reason


def test_guard_allows_subqueries():
    """Test that subqueries are allowed."""
    sql = "SELECT * FROM (SELECT * FROM trains WHERE zone = 'WR') WHERE number = '12002'"
    is_safe, reason = guard_sql(sql)
    assert is_safe is True


def test_guard_allows_joins():
    """Test that JOINs are allowed."""
    sql = """
    SELECT t.* FROM trains t 
    JOIN stops s ON t.number = s.train_number 
    WHERE s.station_code = 'NDLS'
    """
    is_safe, reason = guard_sql(sql)
    assert is_safe is True
