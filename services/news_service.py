"""뉴스 데이터 관련 서비스"""
import requests
import logging
from flask import current_app
from config import Config

logger = logging.getLogger(__name__)


def fetch_from_backend(endpoint, params):
    """백엔드 API로부터 데이터를 가져옵니다."""
    backend_url = f"{Config.BACKEND_URL}{endpoint}"
    
    try:
        logger.debug(f"Fetching from backend: {backend_url} with params: {params}")
        response = requests.get(
            backend_url, 
            params=params, 
            timeout=Config.REQUEST_TIMEOUT
        )
        response.raise_for_status()
        logger.info(f"Successfully fetched data from {endpoint}")
        return response.json(), None
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to fetch from backend {endpoint}: {e}"
        logger.error(error_msg)
        return None, {"error": error_msg}
