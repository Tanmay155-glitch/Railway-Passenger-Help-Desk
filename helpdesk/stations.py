"""
Station resolution module for Railway Passenger Help Desk.
Handles fuzzy matching of station names to codes.
"""

import sqlite3
import logging
import re
from typing import Dict, List, Optional
from rapidfuzz import fuzz

from helpdesk.config import config, find_data_pack

logger = logging.getLogger(__name__)

# Global cache
_stations = None


def load_stations() -> List[Dict]:
    """Load stations from database."""
    global _stations
    
    if _stations is not None:
        return _stations
    
    db_path = find_data_pack()
    if not db_path:
        logger.error("Database not found")
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT code, name, state, zone FROM stations")
        rows = cursor.fetchall()
        
        _stations = []
        for row in rows:
            _stations.append({
                'code': row[0],
                'name': row[1],
                'state': row[2],
                'zone': row[3]
            })
        
        conn.close()
        
        logger.info(f"Loaded {len(_stations)} stations from database")
        return _stations
        
    except Exception as e:
        logger.error(f"Failed to load stations: {e}")
        return []


def resolve_stations(question: str) -> Dict[str, List[str]]:
    """
    Resolve station mentions in question to station codes.
    
    Uses:
    1. Exact code match (case-insensitive)
    2. Exact name match (case-insensitive)
    3. Fuzzy name match (threshold 85)
    
    Args:
        question: Query text
        
    Returns:
        Dictionary mapping mention -> list of station codes
    """
    stations = load_stations()
    if not stations:
        return {}
    
    # Common patterns for station mentions
    patterns = [
        r'from\s+([A-Za-z][A-Za-z\s]+?)(?:\s+to|\s+at|\s+in|\s+station|\?|$)',
        r'to\s+([A-Za-z][A-Za-z\s]+?)(?:\s+from|\s+at|\s+in|\s+station|\?|$)',
        r'in\s+([A-Za-z][A-Za-z\s]+?)(?:\s+to|\s+from|\s+at|\s+station|\?|$)',
        r'at\s+([A-Za-z][A-Za-z\s]+?)(?:\s+to|\s+from|\s+in|\s+station|\?|$)',
        r'between\s+([A-Za-z][A-Za-z\s]+?)\s+and\s+([A-Za-z][A-Za-z\s]+?)(?:\s+station|\?|$)',
        r'([A-Za-z][A-Za-z\s]+?)\s+station',
        r'trains?\s+(?:from|to|in|at)\s+([A-Za-z][A-Za-z\s]+?)(?:\s+to|\s+from|\s+in|\s+at|\?|$)',
    ]
    
    # Extract potential station mentions
    mentions = []
    for pattern in patterns:
        matches = re.finditer(pattern, question, re.IGNORECASE)
        for match in matches:
            for group in match.groups():
                if group:
                    mentions.append(group.strip())
    
    # Also check for standalone city names (common ones)
    common_cities = ['Delhi', 'Mumbai', 'Kolkata', 'Chennai', 'Bangalore', 
                     'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow']
    
    for city in common_cities:
        if city.lower() in question.lower():
            mentions.append(city)
    
    # Remove duplicates
    mentions = list(set(mentions))
    
    # Resolve each mention
    resolved = {}
    
    for mention in mentions:
        codes = resolve_single_station(mention, stations)
        if codes:
            resolved[mention] = codes
    
    logger.info(f"Resolved {len(resolved)} station mentions: {resolved}")
    return resolved


def resolve_single_station(mention: str, stations: List[Dict]) -> List[str]:
    """
    Resolve a single station mention to codes.
    
    Args:
        mention: Station name or code
        stations: List of all stations
        
    Returns:
        List of matching station codes
    """
    mention_lower = mention.lower().strip()
    
    # 1. Try exact code match (case-insensitive)
    for station in stations:
        if station['code'] and station['code'].lower() == mention_lower:
            return [station['code']]
    
    # 2. Try exact name match (case-insensitive)
    exact_matches = []
    for station in stations:
        if station['name'] and station['name'].lower() == mention_lower:
            exact_matches.append(station['code'])
    
    if exact_matches:
        return exact_matches
    
    # 3. Try fuzzy name match
    fuzzy_matches = []
    for station in stations:
        if not station['name']:
            continue
        
        # Compute similarity
        score = fuzz.ratio(mention_lower, station['name'].lower())
        
        if score >= 85:  # Threshold
            fuzzy_matches.append((station['code'], score))
    
    if fuzzy_matches:
        # Sort by score
        fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Return top matches (max 5 for multi-station cities)
        return [code for code, score in fuzzy_matches[:5]]
    
    # 4. Try partial match for common abbreviations
    partial_matches = []
    for station in stations:
        if not station['name']:
            continue
        
        # Check if mention is in station name or vice versa
        if (mention_lower in station['name'].lower() or 
            station['name'].lower() in mention_lower):
            partial_matches.append(station['code'])
    
    if partial_matches:
        return partial_matches[:5]
    
    logger.debug(f"No matches found for: {mention}")
    return []


def get_station_name(code: str) -> Optional[str]:
    """
    Get station name from code.
    
    Args:
        code: Station code
        
    Returns:
        Station name or None
    """
    stations = load_stations()
    
    for station in stations:
        if station['code'] == code:
            return station['name']
    
    return None
