"""
Entity extraction module for Railway Passenger Help Desk.
Extracts identifiers from text: rules, circulars, gazettes, trains, amounts.
"""

import re
from typing import Dict, List


def extract_identifiers(text: str) -> Dict[str, List[str]]:
    """
    Extract identifiers from text using regex patterns.
    
    Args:
        text: Input text to extract from
        
    Returns:
        Dictionary with lists of extracted identifiers:
        - rules: ["Rule 25", ...]
        - circulars: ["CC08/2025", ...]
        - gazettes: ["G.S.R. 41(E)", ...]
        - trains: ["12002", "11039-Slip", ...]
        - amounts: ["₹240", "30%", ...]
    """
    identifiers = {
        "rules": [],
        "circulars": [],
        "gazettes": [],
        "trains": [],
        "amounts": []
    }
    
    # Extract Rule numbers: "Rule 25", "Rule 25A"
    rule_pattern = r'Rule\s+\d+[A-Z]?'
    identifiers["rules"] = list(set(re.findall(rule_pattern, text, re.IGNORECASE)))
    
    # Extract Circular numbers: "CC08/2025", "CC 08 / 2025", "Circular 08 of 2025"
    circular_patterns = [
        r'C[CG]\s*\d+\s*/\s*\d{4}',
        r'Circular\s+\w+\s+of\s+\d{4}'
    ]
    for pattern in circular_patterns:
        identifiers["circulars"].extend(re.findall(pattern, text, re.IGNORECASE))
    identifiers["circulars"] = list(set(identifiers["circulars"]))
    
    # Extract Gazette numbers: "G.S.R. 41(E)"
    gazette_pattern = r'G\.S\.R\.\s+\d+\([A-Z]\)'
    identifiers["gazettes"] = list(set(re.findall(gazette_pattern, text)))
    
    # Extract train numbers: 5 digits, optionally with -Slip
    train_pattern = r'\b\d{5}(?:-Slip)?\b'
    identifiers["trains"] = list(set(re.findall(train_pattern, text)))
    
    # Extract amounts: "₹240", "Rs 240", "240 rupees", "30%"
    amount_patterns = [
        r'₹\s*\d+(?:,\d+)*',
        r'Rs\.?\s+\d+(?:,\d+)*',
        r'\d+\s*%'
    ]
    for pattern in amount_patterns:
        identifiers["amounts"].extend(re.findall(pattern, text))
    identifiers["amounts"] = list(set(identifiers["amounts"]))
    
    return identifiers


def has_exact_match(query_ids: Dict[str, List[str]], chunk_ids: Dict[str, List[str]]) -> bool:
    """
    Check if there's any exact match between query identifiers and chunk identifiers.
    
    Args:
        query_ids: Identifiers extracted from query
        chunk_ids: Identifiers extracted from chunk
        
    Returns:
        True if any identifier matches
    """
    for key in ["rules", "circulars", "gazettes", "trains", "amounts"]:
        query_set = set(s.lower() for s in query_ids.get(key, []))
        chunk_set = set(s.lower() for s in chunk_ids.get(key, []))
        
        if query_set & chunk_set:  # Intersection
            return True
    
    return False
