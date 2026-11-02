"""
LLM client module for Railway Passenger Help Desk.
Handles Gemini API calls with retry logic and rate limiting.
"""

import time
import random
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import google.generativeai as genai

from helpdesk.config import config

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Gemini API client with rate limiting, retry logic, and optional caching.
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (defaults to config)
            model: Model name (defaults to config)
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        self.model_name = model or config.GEMINI_MODEL
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not set. Create .env file with your API key.")
        
        # Configure the API (never log the key)
        genai.configure(api_key=self.api_key)
        
        # Rate limiting: free tier is ~15 RPM
        self.last_request_time = 0
        self.min_request_interval = 4.0  # 15 requests per minute = 4 seconds between requests
        
        # Optional cache directory
        self.cache_dir = config.INDEX_DIR / "cache"
        self.cache_enabled = False  # Enable manually for development
        
        if self.cache_enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, model: str, prompt: str) -> str:
        """Generate cache key from model and prompt."""
        content = f"{model}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Try to get cached response."""
        if not self.cache_enabled:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    logger.debug(f"Cache hit for key {cache_key[:8]}...")
                    return cached.get("response")
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
        
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache a response."""
        if not self.cache_enabled:
            return
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({"response": response}, f)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    def generate(
        self,
        prompt: str,
        schema: Optional[Dict] = None,
        temperature: float = None,
        timeout: int = None
    ) -> str:
        """
        Generate text using Gemini with retry logic.
        
        Args:
            prompt: Input prompt
            schema: Optional JSON schema for structured output
            temperature: Temperature (defaults to config)
            timeout: Timeout in seconds (defaults to config)
            
        Returns:
            Generated text
            
        Raises:
            Exception: If all retries fail
        """
        temperature = temperature if temperature is not None else config.TEMPERATURE
        timeout = timeout or config.TIMEOUT_SECONDS
        
        # Check cache
        cache_key = self._get_cache_key(self.model_name, prompt)
        cached = self._get_cached_response(cache_key)
        if cached:
            return cached
        
        # Retry logic with exponential backoff
        max_retries = config.MAX_RETRIES
        base_delay = 2.0
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                self._wait_for_rate_limit()
                
                # Create model
                model = genai.GenerativeModel(self.model_name)
                
                # Generation config
                gen_config = {
                    "temperature": temperature,
                    "max_output_tokens": 2048,
                }
                
                # Use JSON mode if schema provided
                if schema:
                    gen_config["response_mime_type"] = "application/json"
                
                # Generate
                response = model.generate_content(
                    prompt,
                    generation_config=gen_config
                )
                
                result = response.text
                
                # Cache the response
                self._cache_response(cache_key, result)
                
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if we should retry
                should_retry = (
                    "429" in error_str or  # Rate limit
                    "500" in error_str or  # Server error
                    "503" in error_str or  # Service unavailable
                    "timeout" in error_str
                )
                
                if not should_retry or attempt == max_retries - 1:
                    # Model not found - give helpful error
                    if "404" in error_str or "not found" in error_str:
                        logger.error(
                            f"Model {self.model_name} not found. "
                            f"Set GEMINI_MODEL in .env to a valid model name."
                        )
                    raise
                
                # Calculate backoff with jitter
                delay = base_delay * (2 ** attempt)
                jitter = random.uniform(-0.1, 0.1) * delay
                sleep_time = delay + jitter
                
                # Check for retry_delay hint in error
                if hasattr(e, 'retry_delay'):
                    sleep_time = e.retry_delay
                
                logger.warning(
                    f"API error (attempt {attempt + 1}/{max_retries}): {e}. "
                    f"Retrying in {sleep_time:.1f}s..."
                )
                time.sleep(sleep_time)
        
        raise Exception(f"Failed after {max_retries} retries")
    
    def embed(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding using Gemini embedding endpoint.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector, or None on failure
        """
        try:
            self._wait_for_rate_limit()
            
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )
            
            return result['embedding']
            
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
            return None
