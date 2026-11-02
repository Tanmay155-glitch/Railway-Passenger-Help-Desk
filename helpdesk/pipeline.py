"""
Main pipeline module for Railway Passenger Help Desk.
Orchestrates routing and answer generation.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


def ask(question: str) -> Dict:
    """
    Answer a passenger question using the data pack.
    
    This is the main entry point that routes questions to appropriate
    handlers (document search, database query, or both) and returns
    a structured response.
    
    Args:
        question: Passenger question as text
        
    Returns:
        Dictionary with keys:
        - answer (str): Plain language answer
        - sources (list): List of {"doc": str, "page": int|None}
        - sql (str|None): Executed SQL query if applicable
        - dont_know (bool): True if declining to answer
        
    Note:
        Never raises exceptions. All errors return dont_know=True.
    """
    try:
        # TODO: Implement full pipeline
        # For now, return a stub response
        return {
            "answer": "System not yet fully implemented. Please run build_index.py first, then implement the full pipeline.",
            "sources": [],
            "sql": None,
            "dont_know": True
        }
        
    except Exception as e:
        logger.error(f"Error in ask(): {e}", exc_info=True)
        return {
            "answer": f"Internal error: {str(e)}",
            "sources": [],
            "sql": None,
            "dont_know": True
        }
