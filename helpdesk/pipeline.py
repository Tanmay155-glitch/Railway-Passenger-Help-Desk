"""
Main pipeline module for Railway Passenger Help Desk.
Orchestrates routing and answer generation.
"""

import logging
from typing import Dict

from helpdesk.llm import GeminiClient
from helpdesk.router import route_question
from helpdesk.search import search_with_context
from helpdesk.answer import generate_answer
from helpdesk.sql import answer_with_sql
from helpdesk.config import config

logger = logging.getLogger(__name__)


def answer_from_docs(question: str, llm_client: GeminiClient) -> Dict:
    """
    Answer question using document search.
    
    Args:
        question: User question
        llm_client: LLM client
        
    Returns:
        Response dictionary
    """
    try:
        # Search for relevant chunks with neighbors
        results, neighbors = search_with_context(question, k=5)
        
        if not results:
            return {
                "answer": "I couldn't find relevant information in the documents for this question.",
                "sources": [],
                "sql": None,
                "dont_know": True
            }
        
        # Check retrieval quality
        top_score = results[0].get('score', 0) if results else 0
        if top_score < config.DONT_KNOW_THRESHOLD:
            return {
                "answer": "I don't have enough confidence in the retrieved information to answer this question.",
                "sources": [],
                "sql": None,
                "dont_know": True
            }
        
        # Combine results and neighbors for context expansion
        all_chunks = results + neighbors
        
        logger.debug(f"Passing {len(results)} main chunks + {len(neighbors)} neighbor chunks to answer generation")
        
        # Generate answer with expanded context
        answer_text, sources, sufficient = generate_answer(question, all_chunks, llm_client)
        
        return {
            "answer": answer_text,
            "sources": sources,
            "sql": None,
            "dont_know": not sufficient
        }
        
    except Exception as e:
        logger.error(f"Error in answer_from_docs: {e}", exc_info=True)
        return {
            "answer": f"Error searching documents: {str(e)}",
            "sources": [],
            "sql": None,
            "dont_know": True
        }


def answer_from_db(question: str, llm_client: GeminiClient) -> Dict:
    """
    Answer question using database query.
    
    Args:
        question: User question
        llm_client: LLM client
        
    Returns:
        Response dictionary
    """
    try:
        sql, answer_text, dont_know = answer_with_sql(question, llm_client)
        
        return {
            "answer": answer_text,
            "sources": [],
            "sql": sql,
            "dont_know": dont_know
        }
        
    except Exception as e:
        logger.error(f"Error in answer_from_db: {e}", exc_info=True)
        return {
            "answer": f"Error querying database: {str(e)}",
            "sources": [],
            "sql": None,
            "dont_know": True
        }


def answer_from_both(question: str, llm_client: GeminiClient) -> Dict:
    """
    Answer question using both documents and database.
    
    Args:
        question: User question
        llm_client: LLM client
        
    Returns:
        Response dictionary
    """
    try:
        # Get both results
        doc_result = answer_from_docs(question, llm_client)
        db_result = answer_from_db(question, llm_client)
        
        # If both failed, return don't know
        if doc_result["dont_know"] and db_result["dont_know"]:
            return {
                "answer": "I couldn't find information in either the documents or the timetable database for this question.",
                "sources": [],
                "sql": None,
                "dont_know": True
            }
        
        # If one succeeded, return it
        if doc_result["dont_know"] and not db_result["dont_know"]:
            return db_result
        
        if db_result["dont_know"] and not doc_result["dont_know"]:
            return doc_result
        
        # Both succeeded - merge
        # Use LLM to combine answers
        merge_prompt = f"""Combine these two answers into one coherent response:

ANSWER FROM DOCUMENTS: {doc_result['answer']}

ANSWER FROM TIMETABLE: {db_result['answer']}

QUESTION: {question}

Provide a single, cohesive answer that includes both pieces of information.
Be concise (2-4 sentences)."""
        
        try:
            merged_answer = llm_client.generate(merge_prompt, temperature=0.0)
        except:
            # Fallback: simple concatenation
            merged_answer = f"{doc_result['answer']} {db_result['answer']}"
        
        return {
            "answer": merged_answer,
            "sources": doc_result["sources"],
            "sql": db_result["sql"],
            "dont_know": False
        }
        
    except Exception as e:
        logger.error(f"Error in answer_from_both: {e}", exc_info=True)
        return {
            "answer": f"Error processing question: {str(e)}",
            "sources": [],
            "sql": None,
            "dont_know": True
        }


def refuse(question: str, reason: str) -> Dict:
    """
    Generate polite refusal.
    
    Args:
        question: User question
        reason: Refusal reason (out_of_scope or refuse)
        
    Returns:
        Response dictionary
    """
    if reason == "out_of_scope":
        answer = ("I can only answer questions about railway rules and timetables from the 2016 data. "
                  "I don't have information about fares, seat availability, PNR status, waitlist confirmation, "
                  "or live running status. Is there something else I can help you with?")
    
    elif reason == "refuse":
        answer = "I cannot modify the database. I can only retrieve information from documents and timetables."
    
    else:
        answer = "I'm not able to answer this question."
    
    return {
        "answer": answer,
        "sources": [],
        "sql": None,
        "dont_know": True
    }


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
        # Validate input
        if not question or not question.strip():
            return {
                "answer": "Please provide a question.",
                "sources": [],
                "sql": None,
                "dont_know": True
            }
        
        # Initialize LLM client
        try:
            llm_client = GeminiClient()
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            return {
                "answer": f"System initialization failed: {str(e)}. Please check your .env file.",
                "sources": [],
                "sql": None,
                "dont_know": True
            }
        
        # Route question
        route = route_question(question, llm_client)
        logger.info(f"Question routed to: {route}")
        
        # Handle based on route
        if route == "docs":
            return answer_from_docs(question, llm_client)
        
        elif route == "db":
            return answer_from_db(question, llm_client)
        
        elif route == "both":
            return answer_from_both(question, llm_client)
        
        elif route in ["out_of_scope", "refuse"]:
            return refuse(question, route)
        
        else:
            # Unknown route, default to docs
            logger.warning(f"Unknown route: {route}, defaulting to docs")
            return answer_from_docs(question, llm_client)
        
    except Exception as e:
        logger.error(f"Error in ask(): {e}", exc_info=True)
        return {
            "answer": f"Internal error: {str(e)}",
            "sources": [],
            "sql": None,
            "dont_know": True
        }
