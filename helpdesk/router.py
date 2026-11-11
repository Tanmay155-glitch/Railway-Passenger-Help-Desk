"""
Router module for Railway Passenger Help Desk.
Routes questions to appropriate handlers: docs, db, both, or refuse.
"""

import json
import logging
import re
from typing import Tuple,Optional

from helpdesk.llm import GeminiClient

logger = logging.getLogger(__name__)


# LLM routing prompt
ROUTE_PROMPT = """Classify this railway passenger question into ONE category:

CATEGORIES:
1. "docs" - Questions about rules, refunds, cancellation charges, Tatkal booking, advance reservation periods, chart preparation times, general policies
2. "db" - Questions about train schedules, timings, stations, routes, train numbers, stops, travel duration  
3. "both" - Questions mixing rules AND specific trains/times (e.g., "refund for train 12002 cancelled 10 hours before")
4. "out_of_scope" - Questions about fares/prices, seat availability, PNR status, waitlist confirmation, live running status, anything requiring data we don't have
5. "refuse" - Requests to change/update/delete data, or any data modification

EXAMPLES:
- "What is the Tatkal cancellation charge?" → docs
- "Which trains go from Delhi to Mumbai?" → db
- "What is the refund for train 12002 if cancelled?" → both (needs train type from db + refund rules from docs)
- "How much is a ticket from Delhi to Mumbai?" → out_of_scope (no fare data)
- "What is my PNR status?" → out_of_scope (no PNR data)
- "Change the departure time of train 12002" → refuse (data modification)
- "Will my waitlisted ticket get confirmed?" → out_of_scope (prediction, no data)

QUESTION: {question}

Return JSON:
{{
  "route": "docs|db|both|out_of_scope|refuse",
  "confidence": 0.95,
  "reason": "brief explanation"
}}

Your response:"""


def route_by_keywords(question: str) -> Tuple[Optional[str], str]:
    """
    Fast keyword-based routing.
    
    Args:
        question: User question
        
    Returns:
        Tuple of (route or None, reason)
    """
    question_lower = question.lower()
    
    # Refuse keywords (data modification)
    refuse_keywords = ['change', 'update', 'delete', 'modify', 'set', 'alter', 'remove']
    for keyword in refuse_keywords:
        if keyword in question_lower:
            # Check if it's a "how to" question (not an action)
            if 'how to' not in question_lower and 'can i' not in question_lower:
                return 'refuse', f"Detected write verb: {keyword}"
    
    # Out of scope keywords
    out_of_scope_keywords = [
        'fare', 'price', 'cost', 'ticket price',
        'pnr', 'pnr status',
        'seat availability', 'available seats', 'berth available',
        'waitlist', 'waiting list', 'rac', 'will confirm', 'get confirmed',
        'live status', 'running status', 'current location', 'where is train',
        'platform number', 'which platform'
    ]
    
    for keyword in out_of_scope_keywords:
        if keyword in question_lower:
            return 'out_of_scope', f"Out of scope keyword: {keyword}"
    
    # Database keywords (timetable)
    db_keywords = [
        'train', 'trains', 'schedule', 'timing', 'departure', 'arrival',
        'station', 'stops', 'route', 'from', 'to', 'between',
        'which trains', 'how many trains', 'train number'
    ]
    
    # Check for train number pattern (5 digits)
    has_train_number = bool(re.search(r'\b\d{5}\b', question))
    
    db_score = sum(1 for kw in db_keywords if kw in question_lower)
    if has_train_number:
        db_score += 2
    
    # Document keywords (rules)
    doc_keywords = [
        'refund', 'cancellation', 'cancel', 'charge',
        'tatkal', 'rule', 'circular', 'policy',
        'advance reservation', 'booking period', 'booking limit',
        'chart', 'reservation chart',
        'aadhaar', 'id proof',
        'tdr', 'ticket deposit receipt'
    ]
    
    doc_score = sum(1 for kw in doc_keywords if kw in question_lower)
    
    # Check for specific rule/circular patterns
    has_rule_ref = bool(re.search(r'rule\s+\d+', question_lower))
    has_circular_ref = bool(re.search(r'circular|cc\s*\d+', question_lower))
    
    if has_rule_ref or has_circular_ref:
        doc_score += 2
    
    # Decide based on scores
    if db_score > 0 and doc_score > 0:
        return 'both', f"Both DB keywords ({db_score}) and doc keywords ({doc_score})"
    
    if db_score >= 2:
        return 'db', f"Strong DB signal (score: {db_score})"
    
    if doc_score >= 2:
        return 'docs', f"Strong docs signal (score: {doc_score})"
    
    # Ambiguous - let LLM decide
    return None, f"Ambiguous (db: {db_score}, docs: {doc_score})"


def route_by_llm(question: str, llm_client: GeminiClient) -> Tuple[str, float, str]:
    """
    LLM-based routing for ambiguous cases.
    
    Args:
        question: User question
        llm_client: LLM client
        
    Returns:
        Tuple of (route, confidence, reason)
    """
    prompt = ROUTE_PROMPT.format(question=question)
    
    try:
        response = llm_client.generate(prompt, temperature=0.0)
        
        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()
                data = json.loads(response)
            elif '```' in response:
                json_start = response.find('```') + 3
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()
                data = json.loads(response)
            else:
                # Fallback
                return 'docs', 0.5, "JSON parse failed, defaulting to docs"
        
        route = data.get('route', 'docs')
        confidence = float(data.get('confidence', 0.5))
        reason = data.get('reason', '')
        
        return route, confidence, reason
        
    except Exception as e:
        logger.error(f"LLM routing failed: {e}")
        return 'docs', 0.5, f"LLM routing failed: {e}"


def route_question(question: str, llm_client: GeminiClient = None) -> str:
    """
    Route question to appropriate handler.
    
    Uses keyword-based routing first (fast), then LLM for ambiguous cases.
    
    Args:
        question: User question
        llm_client: LLM client (optional, created if needed)
        
    Returns:
        Route string: "docs", "db", "both", "out_of_scope", or "refuse"
    """
    # Fast keyword routing
    keyword_route, reason = route_by_keywords(question)
    
    if keyword_route is not None:
        logger.info(f"Route: {keyword_route} (keyword-based: {reason})")
        return keyword_route
    
    # Ambiguous - use LLM
    if llm_client is None:
        try:
            llm_client = GeminiClient()
        except Exception as e:
            logger.error(f"Failed to create LLM client for routing: {e}")
            # Default to docs as safest option
            return 'docs'
    
    route, confidence, llm_reason = route_by_llm(question, llm_client)
    
    # Apply confidence threshold
    if confidence < 0.5:
        logger.warning(f"Low confidence ({confidence}), defaulting to docs")
        route = 'docs'
    
    logger.info(f"Route: {route} (LLM-based, confidence: {confidence:.2f}, reason: {llm_reason})")
    
    return route
