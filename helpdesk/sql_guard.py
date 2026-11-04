"""
SQL safety guard module for Railway Passenger Help Desk.
Multiple layers of defense against SQL injection and unsafe queries.
"""

import re
import sqlite3
import time
import logging
from typing import Tuple, List, Optional
from pathlib import Path

from helpdesk.config import config

logger = logging.getLogger(__name__)


# Forbidden keywords (case-insensitive)
FORBIDDEN_KEYWORDS = [
    'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE',
    'REPLACE', 'ATTACH', 'DETACH', 'PRAGMA', 'VACUUM',
    'TRUNCATE', 'RENAME', 'REINDEX'
]


def guard_sql(sql: str) -> Tuple[bool, str]:
    """
    Check if SQL is safe to execute.
    
    Returns (True, "") if safe, (False, reason) if rejected.
    
    Args:
        sql: SQL query to check
        
    Returns:
        Tuple of (is_safe, reason)
    """
    if not sql or not sql.strip():
        return False, "Empty SQL query"
    
    sql = sql.strip()
    
    # Layer 1: Strip comments
    sql_no_comments = strip_comments(sql)
    
    # Layer 2: Check for multiple statements
    statements = sql_no_comments.split(';')
    statements = [s.strip() for s in statements if s.strip()]
    
    if len(statements) > 1:
        return False, "Multiple statements not allowed"
    
    sql_clean = statements[0]
    
    # Layer 3: Check first keyword
    tokens = sql_clean.split()
    if not tokens:
        return False, "Empty SQL after cleanup"
    
    first_keyword = tokens[0].upper()
    
    if first_keyword not in ['SELECT', 'WITH']:
        return False, f"Only SELECT or WITH allowed, got {first_keyword}"
    
    # Layer 4: Check for forbidden keywords
    sql_upper = sql_clean.upper()
    
    for keyword in FORBIDDEN_KEYWORDS:
        # Use word boundaries to avoid false positives
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, sql_upper):
            return False, f"Forbidden keyword: {keyword}"
    
    # Layer 5: Check for suspicious patterns
    suspicious = [
        r'--',  # Comment
        r'/\*',  # Block comment start
        r'\*/',  # Block comment end
        r';\s*SELECT',  # Statement after semicolon
        r'UNION.*SELECT',  # UNION injection
    ]
    
    for pattern in suspicious:
        if re.search(pattern, sql_upper):
            return False, f"Suspicious pattern: {pattern}"
    
    return True, ""


def strip_comments(sql: str) -> str:
    """
    Remove SQL comments (-- and /* */).
    
    Args:
        sql: SQL with possible comments
        
    Returns:
        SQL with comments removed
    """
    # Remove single-line comments (--) 
    sql = re.sub(r'--[^\n]*', '', sql)
    
    # Remove multi-line comments (/* */)
    sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
    
    return sql


def wrap_with_limit(sql: str, limit: int = None) -> str:
    """
    Wrap SQL with LIMIT if not already present.
    
    Args:
        sql: Original SQL
        limit: Row limit (default from config)
        
    Returns:
        SQL with LIMIT
    """
    if limit is None:
        limit = config.SQL_ROW_LIMIT
    
    sql_upper = sql.upper()
    
    # Check if LIMIT already exists
    if 'LIMIT' in sql_upper:
        # Extract existing limit
        match = re.search(r'LIMIT\s+(\d+)', sql_upper)
        if match:
            existing_limit = int(match.group(1))
            if existing_limit <= limit:
                return sql  # Use existing smaller limit
    
    # Wrap with subquery and LIMIT
    wrapped = f"SELECT * FROM ({sql}) LIMIT {limit}"
    return wrapped


def execute_safe_sql(
    sql: str,
    db_path: Path,
    timeout_ms: int = None
) -> Tuple[List[List], List[str]]:
    """
    Execute SQL with multiple safety layers.
    
    Args:
        sql: SQL query to execute
        db_path: Path to database
        timeout_ms: Timeout in milliseconds (default from config)
        
    Returns:
        Tuple of (rows, column_names)
        
    Raises:
        ValueError: If SQL is unsafe
        sqlite3.Error: If execution fails
    """
    if timeout_ms is None:
        timeout_ms = config.SQL_TIMEOUT_MS
    
    # Strip trailing semicolons first (some models add them)
    sql = sql.strip().rstrip(';').strip()
    
    # Guard check
    is_safe, reason = guard_sql(sql)
    if not is_safe:
        raise ValueError(f"Unsafe SQL rejected: {reason}")
    
    # Wrap with LIMIT
    sql = wrap_with_limit(sql)
    
    # Open in read-only mode
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    
    try:
        # Layer 1: Enable query_only mode
        conn.execute("PRAGMA query_only = ON")
        
        # Layer 2: Set authorizer
        def authorizer(action, arg1, arg2, db, trigger):
            """Allow only SELECT, READ, and FUNCTION."""
            allowed = [
                sqlite3.SQLITE_SELECT,
                sqlite3.SQLITE_READ,
                sqlite3.SQLITE_FUNCTION
            ]
            
            if action in allowed:
                return sqlite3.SQLITE_OK
            else:
                logger.warning(f"Authorizer denied action: {action}")
                return sqlite3.SQLITE_DENY
        
        conn.set_authorizer(authorizer)
        
        # Layer 3: Set progress handler for timeout
        start_time = time.time()
        timeout_seconds = timeout_ms / 1000.0
        
        def check_timeout():
            """Return non-zero to abort."""
            if time.time() - start_time > timeout_seconds:
                logger.warning(f"Query timeout after {timeout_seconds}s")
                return 1  # Abort
            return 0  # Continue
        
        conn.set_progress_handler(check_timeout, 100)  # Check every 100 VM instructions
        
        # Execute query
        cursor = conn.cursor()
        cursor.execute(sql)
        
        # Fetch results
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        logger.info(f"Query returned {len(rows)} rows")
        
        return rows, columns
        
    finally:
        conn.close()
