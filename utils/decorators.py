"""데코레이터 유틸리티"""
import time
import logging
from functools import wraps
from config import Config

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=None, backoff_factor=None):
    """재시도 로직 데코레이터"""
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
    if backoff_factor is None:
        backoff_factor = Config.BACKOFF_FACTOR
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Final attempt failed for {func.__name__}: {str(e)}")
                        raise e
                    
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator


def track_performance(endpoint):
    """성능 추적 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from utils.metrics import metrics
            
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                metrics['request_count'][endpoint] += 1
                response_time = time.time() - start_time
                metrics['response_times'][endpoint].append(response_time)
                logger.info(f"{endpoint} completed in {response_time:.3f}s")
                return result
            except Exception as e:
                metrics['errors'][endpoint] += 1
                logger.error(f"Error in {endpoint}: {str(e)}")
                raise
        return wrapper
    return decorator
