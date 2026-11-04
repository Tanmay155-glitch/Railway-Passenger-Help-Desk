"""
Answer generation module for Railway Passenger Help Desk.
Generates grounded answers with source citations from retrieved chunks.
"""

import json
import logging
from typing import List, Dict, Tuple
from datetime import datetime

from helpdesk.llm import GeminiClient
from helpdesk.config import config

logger = logging.getLogger(__name__)


# Answer generation prompt template
ANSWER_PROMPT = """You are a railway helpdesk assistant. Answer this question using ONLY the provided document chunks.

STRICT RULES:
1. Answer ONLY from the supplied chunks below. Do not use your training data.
2. Quote numbers, dates, amounts, and times EXACTLY as they appear in the chunks.
3. If two documents conflict (different dates), use the LATER-DATED document and mention it replaces the older one.
4. If a rule exists for a SPECIFIC TRAIN TYPE (e.g., "Vande Bharat Sleeper"), it OVERRIDES the general rule for that train type.
5. The "Pre revised" column in the 2015 table is HISTORY, not current rules. Use only "Revised" column.
6. PIB statements phrased as future ("soon", "will be") should be reported as ANNOUNCED, not yet in force.
7. If the chunks don't contain enough information to answer, set sufficient=false.
8. Cite the chunk_ids you actually used.

DOCUMENT CHUNKS:
{chunks_text}

QUESTION: {question}

Return your response as JSON with this exact structure:
{{
  "answer": "Your plain language answer here (2-6 sentences)",
  "chunk_ids_used": ["chunk_id1", "chunk_id2"],
  "sufficient": true
}}

Your response:"""


def apply_precedence(chunks: List[Dict]) -> List[Dict]:
    """
    Sort chunks by date when they cover the same topic.
    Newer documents take precedence over older ones.
    
    Args:
        chunks: List of retrieved chunks
        
    Returns:
        Chunks sorted with precedence metadata
    """
    # Group by document
    by_doc = {}
    for chunk in chunks:
        doc = chunk.get('doc', '')
        if doc not in by_doc:
            by_doc[doc] = []
        by_doc[doc].append(chunk)
    
    # If only one document, no precedence needed
    if len(by_doc) <= 1:
        return chunks
    
    # Sort documents by date
    doc_dates = {}
    for doc, doc_chunks in by_doc.items():
        date_str = doc_chunks[0].get('date', '2000-01-01')
        doc_dates[doc] = date_str
    
    sorted_docs = sorted(doc_dates.items(), key=lambda x: x[1], reverse=True)
    
    # Mark precedence
    enhanced = []
    for rank, (doc, date) in enumerate(sorted_docs, 1):
        for chunk in by_doc[doc]:
            chunk = chunk.copy()
            chunk['precedence_rank'] = rank
            chunk['precedence_date'] = date
            if rank == 1:
                chunk['is_latest_doc'] = True
            enhanced.append(chunk)
    
    return enhanced


def build_sources(chunk_ids: List[str], all_chunks: List[Dict]) -> List[Dict]:
    """
    Build source citations from chunk IDs.
    
    Args:
        chunk_ids: List of chunk IDs the LLM used
        all_chunks: All retrieved chunks
        
    Returns:
        List of {"doc": str, "page": int|None} citations
    """
    # Map chunk_id to chunk
    chunk_map = {c.get('chunk_id', ''): c for c in all_chunks}
    
    # Extract sources
    sources = []
    seen = set()
    
    for chunk_id in chunk_ids:
        chunk = chunk_map.get(chunk_id)
        if not chunk:
            logger.warning(f"Chunk ID not found: {chunk_id}")
            continue
        
        doc = chunk.get('doc', '')
        page = chunk.get('page')
        
        # Create source key
        source_key = (doc, page)
        
        if source_key not in seen:
            sources.append({
                "doc": doc,
                "page": page
            })
            seen.add(source_key)
    
    # Limit to 2-4 sources
    if len(sources) > 4:
        sources = sources[:4]
    
    return sources


def format_chunks_for_prompt(chunks: List[Dict]) -> str:
    """
    Format chunks into a readable text for the LLM prompt.
    
    Args:
        chunks: List of chunks with metadata
        
    Returns:
        Formatted text
    """
    formatted_parts = []
    
    for i, chunk in enumerate(chunks, 1):
        chunk_id = chunk.get('chunk_id', f'chunk_{i}')
        doc = chunk.get('doc', 'unknown')
        page = chunk.get('page', 'N/A')
        date = chunk.get('date', 'unknown')
        issuer = chunk.get('issuer', 'unknown')
        text = chunk.get('text', chunk.get('text_for_embedding', ''))
        
        # Add precedence info if available
        precedence = ""
        if chunk.get('is_latest_doc'):
            precedence = " [LATEST DOCUMENT]"
        elif chunk.get('precedence_rank', 1) > 1:
            precedence = f" [OLDER DOCUMENT - Date: {date}]"
        
        part = f"""
--- Chunk {i} (ID: {chunk_id}) ---
Document: {doc}
Page: {page}
Issuer: {issuer}
Date: {date}{precedence}

{text}
"""
        formatted_parts.append(part)
    
    return "\n".join(formatted_parts)


def generate_answer(
    question: str,
    chunks: List[Dict],
    llm_client: GeminiClient
) -> Tuple[str, List[Dict], bool]:
    """
    Generate grounded answer from retrieved chunks.
    
    Args:
        question: User question
        chunks: Retrieved chunks with metadata
        llm_client: LLM client
        
    Returns:
        Tuple of (answer_text, source_citations, sufficient_flag)
    """
    if not chunks:
        return (
            "I don't have enough information to answer this question. It may not be covered in the available documents.",
            [],
            False
        )
    
    # Apply precedence logic
    chunks = apply_precedence(chunks)
    
    # Format chunks for prompt
    chunks_text = format_chunks_for_prompt(chunks)
    
    # Build prompt
    prompt = ANSWER_PROMPT.format(
        chunks_text=chunks_text,
        question=question
    )
    
    try:
        # JSON schema for structured output
        answer_schema = {
            "type": "object",
            "properties": {
                "answer": {"type": "string"},
                "chunk_ids_used": {"type": "array", "items": {"type": "integer"}},
                "sufficient": {"type": "boolean"}
            },
            "required": ["answer", "chunk_ids_used", "sufficient"]
        }
        
        # Generate answer with JSON schema
        response = llm_client.generate(prompt, schema=answer_schema, temperature=0.0)
        
        # Parse JSON response
        try:
            response_data = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()
                response_data = json.loads(response)
            elif '```' in response:
                json_start = response.find('```') + 3
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()
                response_data = json.loads(response)
            else:
                raise
        
        answer_text = response_data.get('answer', '')
        chunk_ids_used = response_data.get('chunk_ids_used', [])
        sufficient = response_data.get('sufficient', True)
        
        # Build sources from chunk IDs
        sources = build_sources(chunk_ids_used, chunks)
        
        # If not sufficient, update answer
        if not sufficient:
            if not answer_text.startswith("I don't"):
                answer_text = "I don't have enough information to answer this fully. " + answer_text
            return (answer_text, sources, False)
        
        logger.info(f"Generated answer with {len(sources)} sources")
        return (answer_text, sources, True)
        
    except Exception as e:
        logger.error(f"Answer generation failed: {e}", exc_info=True)
        return (
            f"Error generating answer: {str(e)}",
            [],
            False
        )


def compute_refund_percentage(
    hours_to_departure: float,
    train_type: str,
    chunks: List[Dict]
) -> Tuple[Optional[float], Optional[str]]:
    """
    Compute refund percentage based on hours to departure.
    This arithmetic is done in Python, not in the LLM.
    
    Args:
        hours_to_departure: Hours until train departure
        train_type: Type of train (e.g., "Tatkal", "Vande Bharat Sleeper")
        chunks: Chunks containing refund rules
        
    Returns:
        Tuple of (percentage, clause_reference)
    """
    # This is a placeholder for arithmetic computation
    # In full implementation, this would parse the refund rules from chunks
    # and apply the time-bucket logic
    
    # For now, return None to indicate it should be handled by LLM
    # But in production, this extracts rules like:
    # "> 48 hours: 75% refund"
    # "24-48 hours: 50% refund"
    # "< 24 hours: 25% refund"
    # Then computes which bucket hours_to_departure falls into
    
    return None, None
