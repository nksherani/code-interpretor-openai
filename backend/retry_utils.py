"""
Retry utilities for handling OpenAI rate limits
"""
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry_with_exponential_backoff(
    max_retries=3,
    initial_delay=1.0,
    exponential_base=2.0,
    jitter=True
):
    """
    Decorator to retry a function with exponential backoff
    Useful for handling rate limits
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e)
                    
                    # Check if it's a rate limit error
                    if 'rate_limit_exceeded' in error_str.lower() or '429' in error_str:
                        if attempt < max_retries:
                            # Extract wait time from error if available
                            wait_time = delay
                            if 'try again in' in error_str.lower():
                                try:
                                    # Extract milliseconds from error message
                                    import re
                                    match = re.search(r'try again in (\d+)ms', error_str)
                                    if match:
                                        wait_ms = int(match.group(1))
                                        wait_time = max(wait_ms / 1000.0, delay)
                                except:
                                    pass
                            
                            logger.warning(
                                f"Rate limit hit. Retrying in {wait_time:.2f}s... "
                                f"(Attempt {attempt + 1}/{max_retries})"
                            )
                            time.sleep(wait_time)
                            delay *= exponential_base
                            continue
                    
                    # If it's not a rate limit error, raise immediately
                    raise
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator

