"""
Configuration module for Railway Passenger Help Desk.
Contains paths, model parameters, and thresholds.
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class Config:
    """Configuration constants and paths for the helpdesk system."""
    
    # Paths
    DATA_DIR: Path = Path("data")
    INDEX_DIR: Path = Path("index")
    
    # Search parameters
    RETRIEVAL_K: int = 5
    BM25_WEIGHT: float = 0.5
    DENSE_WEIGHT: float = 0.5
    EXACT_MATCH_BOOST: float = 2.0
    
    # LLM parameters
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
    TEMPERATURE: float = 0.0
    TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 3
    
    # SQL safety
    SQL_ROW_LIMIT: int = 50
    SQL_TIMEOUT_MS: int = 5000
    
    # OCR
    OCR_DPI: int = 300
    MIN_TEXT_CHARS: int = 50
    
    # Thresholds
    SUFFICIENCY_THRESHOLD: float = 0.3
    DONT_KNOW_THRESHOLD: float = 0.2


# Global config instance
config = Config()


def find_data_pack() -> Optional[Path]:
    """
    Discover the data pack location by searching for rail_timetable.db.
    Supports both data/rail_capstone_pack/ and data/ layouts.
    
    Returns:
        Path to the database file, or None if not found.
    """
    if not config.DATA_DIR.exists():
        return None
    
    # Search recursively for the database
    db_files = list(config.DATA_DIR.rglob("rail_timetable.db"))
    
    if not db_files:
        return None
    
    return db_files[0]


def find_document(filename: str) -> Optional[Path]:
    """
    Find a document file within the data pack.
    
    Args:
        filename: Name of the document file to find
        
    Returns:
        Path to the document, or None if not found
    """
    if not config.DATA_DIR.exists():
        return None
    
    # Search recursively for the file
    doc_files = list(config.DATA_DIR.rglob(filename))
    
    if not doc_files:
        return None
    
    return doc_files[0]


def validate_environment() -> tuple[bool, list[str]]:
    """
    Validate that the environment is properly configured.
    
    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []
    
    # Check API key
    if not config.GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY not set in .env file. Create .env with your Gemini API key.")
    
    # Check data directory
    if not config.DATA_DIR.exists():
        errors.append(f"Data directory not found at {config.DATA_DIR}. Unzip rail_capstone_pack.zip into data/")
    else:
        # Check for database
        db = find_data_pack()
        if not db:
            errors.append("Database rail_timetable.db not found in data/. Unzip the data pack.")
    
    # Check index directory exists (will be created if needed)
    if not config.INDEX_DIR.exists():
        config.INDEX_DIR.mkdir(parents=True, exist_ok=True)
    
    return (len(errors) == 0, errors)
