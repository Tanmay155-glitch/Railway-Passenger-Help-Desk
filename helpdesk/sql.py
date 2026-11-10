"""
Text-to-SQL module for Railway Passenger Help Desk.
Generates and executes safe SQL queries for timetable questions.
"""

import logging
from typing import Tuple, Optional, Dict, List
from pathlib import Path

from helpdesk.config import config, find_data_pack
from helpdesk.llm import GeminiClient
from helpdesk.stations import resolve_stations, get_station_name
from helpdesk.sql_guard import execute_safe_sql

logger = logging.getLogger(__name__)

# Load schema once
_schema = None


def load_schema() -> str:
    """Load database schema from index."""
    global _schema
    
    if _schema is not None:
        return _schema
    
    schema_file = config.INDEX_DIR / "schema.txt"
    if schema_file.exists():
        with open(schema_file, 'r', encoding='utf-8') as f:
            _schema = f.read()
        logger.info("Loaded database schema")
    else:
        logger.warning(f"Schema file not found: {schema_file}")
        _schema = "-- Schema not available, run build_index.py first"
    
    return _schema


def is_write_request(question: str) -> bool:
    """
    Check if question requests data modification.
    
    Args:
        question: Query text
        
    Returns:
        True if write request detected
    """
    write_verbs = [
        'change', 'update', 'delete', 'remove', 'modify',
        'set', 'alter', 'drop', 'create', 'insert', 'add'
    ]
    
    question_lower = question.lower()
    
    for verb in write_verbs:
        if verb in question_lower:
            # Check context - might be asking "how to change" not "change now"
            if 'how to' in question_lower or 'can i' in question_lower:
                continue  # Question about process, not action
            return True
    
    return False


def generate_sql(
    question: str,
    resolved_stations: Dict[str, List[str]],
    llm_client: GeminiClient,
    schema: str
) -> str:
    """
    Generate SQL query using LLM.
    
    Args:
        question: User question
        resolved_stations: Map of station mentions to codes
        llm_client: LLM client
        schema: Database schema
        
    Returns:
        SQL query string
    """
    # Build prompt
    prompt = f"""You are a SQLite expert. Generate ONE SELECT query for this question.

DATABASE SCHEMA:
{schema}

IMPORTANT RULES:
1. Use the `stops` view (not schedules) for "trains from A to B" questions
   - stops is a view: SELECT * FROM schedules WHERE is_halt = 1
   - It contains only stations where trains actually stop
2. train.number is TEXT (not integer). Keep leading zeros: "12002" not 12002
3. For overnight journeys, use the day column:
   - travel_minutes = (day_arrival - day_departure) * 1440 + minutes(arrival) - minutes(departure)
   - Example: If train departs day 1 at 23:00 and arrives day 2 at 07:00, that's 8 hours
4. Times are stored as TEXT in HH:MM format (e.g., "14:30", "09:05")
5. Station codes are uppercase TEXT (e.g., "NDLS" for New Delhi, "BCT" for Mumbai Central)
6. Many cities have multiple stations (e.g., Chennai has MAS, MS, MSB, etc.)

RESOLVED STATION CODES:
"""
    
    if resolved_stations:
        for mention, codes in resolved_stations.items():
            stations_str = ", ".join(codes)
            prompt += f"- \"{mention}\" → [{stations_str}]\n"
    else:
        prompt += "(No stations resolved from question)\n"
    
    prompt += f"""

QUESTION: {question}

Generate a single SELECT query. Return ONLY the SQL query, no explanations.

EXAMPLES OF QUERY PATTERNS (generic, not answers):
- Trains between two stations: SELECT t.* FROM trains t JOIN stops s1 ON ... JOIN stops s2 ON ...
- Trains departing after a time: WHERE departure > '14:00'
- Count of stops: SELECT COUNT(*) FROM stops WHERE train_number = '12002'
- Train details: SELECT * FROM trains WHERE number = '12002'

Your SQL query:"""
    
    try:
        response = llm_client.generate(prompt, temperature=0.0)
        
        # Extract SQL (remove markdown code blocks if present)
        sql = response.strip()
        if sql.startswith('```'):
            # Remove code block markers
            lines = sql.split('\n')
            sql = '\n'.join(lines[1:-1]) if len(lines) > 2 else sql
            sql = sql.replace('```sql', '').replace('```', '').strip()
        
        logger.info(f"Generated SQL: {sql[:100]}...")
        return sql
        
    except Exception as e:
        logger.error(f"SQL generation failed: {e}")
        raise


def verbalize_results(
    rows: List[List],
    columns: List[str],
    capped: bool,
    question: str
) -> str:
    """
    Convert SQL results to plain language.
    
    Args:
        rows: Query results
        columns: Column names
        capped: Whether results were capped at limit
        question: Original question
        
    Returns:
        Plain language description
    """
    if not rows:
        return ("I found no results in the timetable database. "
                "Note: This is a 2016 snapshot, so recent trains may not be included.")
    
    # Build a simple table-like description
    answer_parts = []
    
    if len(rows) == 1:
        # Single result - describe it
        row_dict = dict(zip(columns, rows[0]))
        
        # Format based on what columns we have
        if 'name' in row_dict and 'number' in row_dict:
            answer_parts.append(f"Train {row_dict['number']} ({row_dict['name']})")
        elif 'count' in columns[0].lower() or 'COUNT' in columns[0]:
            answer_parts.append(f"The count is {rows[0][0]}")
        else:
            # Generic: list key-value pairs
            for col, val in row_dict.items():
                if val is not None:
                    answer_parts.append(f"{col}: {val}")
    
    elif len(rows) <= 5:
        # Few results - list them
        answer_parts.append(f"I found {len(rows)} results:")
        
        for i, row in enumerate(rows, 1):
            row_dict = dict(zip(columns, row))
            
            # Try to identify what this is
            if 'name' in row_dict and 'number' in row_dict:
                answer_parts.append(f"{i}. Train {row_dict['number']} - {row_dict['name']}")
            elif 'name' in row_dict:
                answer_parts.append(f"{i}. {row_dict['name']}")
            else:
                # Just show first 2-3 meaningful columns
                vals = [str(v) for v in row[:min(3, len(row))] if v is not None]
                answer_parts.append(f"{i}. {', '.join(vals)}")
    
    else:
        # Many results - summarize
        answer_parts.append(f"I found {len(rows)} results in the timetable.")
        
        # Try to summarize
        if 'number' in columns:
            numbers = [row[columns.index('number')] for row in rows[:5]]
            answer_parts.append(f"First few train numbers: {', '.join(str(n) for n in numbers)}")
        
        if capped:
            answer_parts.append(f"(Results limited to first {len(rows)} rows)")
    
    # Add dataset note
    answer_parts.append("\nNote: This data is from a 2016 timetable snapshot.")
    
    return " ".join(answer_parts)


def answer_with_sql(question: str, llm_client: GeminiClient = None) -> Tuple[Optional[str], str, bool]:
    """
    Answer a question using text-to-SQL.
    
    Args:
        question: User question
        llm_client: LLM client (created if not provided)
        
    Returns:
        Tuple of (sql, answer_text, dont_know)
    """
    # Check for write requests
    if is_write_request(question):
        return (
            None,
            "I cannot modify the database. I can only retrieve information from the timetable.",
            True
        )
    
    # Get database path
    db_path = find_data_pack()
    if not db_path:
        return (
            None,
            "Database not found. Please ensure the data pack is unzipped into data/",
            True
        )
    
    # Load schema
    schema = load_schema()
    
    # Initialize LLM client if needed
    if llm_client is None:
        try:
            llm_client = GeminiClient()
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return (None, f"LLM initialization failed: {e}", True)
    
    try:
        # Step 1: Resolve station names
        resolved_stations = resolve_stations(question)
        
        # Step 2: Generate SQL
        sql = generate_sql(question, resolved_stations, llm_client, schema)
        
        # Step 3: Execute with safety guards
        try:
            rows, columns = execute_safe_sql(sql, db_path)
            capped = len(rows) == config.SQL_ROW_LIMIT
            
            # Step 4: Verbalize results
            answer = verbalize_results(rows, columns, capped, question)
            
            return (sql, answer, False)
            
        except ValueError as e:
            # SQL guard rejected it
            logger.warning(f"SQL rejected by guard: {e}")
            
            # Try one retry with error message
            retry_prompt = f"""The previous SQL was rejected: {e}

Original question: {question}
Rejected SQL: {sql}

Please generate a SAFE SELECT-only query that follows all rules.
Return ONLY the SQL query:"""
            
            try:
                sql = llm_client.generate(retry_prompt, temperature=0.0)
                sql = sql.strip().replace('```sql', '').replace('```', '').strip()
                
                # Try again
                rows, columns = execute_safe_sql(sql, db_path)
                capped = len(rows) == config.SQL_ROW_LIMIT
                answer = verbalize_results(rows, columns, capped, question)
                
                return (sql, answer, False)
                
            except Exception as retry_error:
                logger.error(f"Retry also failed: {retry_error}")
                return (
                    sql,
                    f"Could not generate a safe query for this question. Error: {retry_error}",
                    True
                )
        
        except Exception as e:
            logger.error(f"SQL execution failed: {e}")
            return (
                sql,
                f"Query execution failed: {e}",
                True
            )
    
    except Exception as e:
        logger.error(f"SQL generation failed: {e}")
        return (
            None,
            f"Failed to generate SQL query: {e}",
            True
        )
