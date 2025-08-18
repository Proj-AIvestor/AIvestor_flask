"""라우트 패키지"""
from .news_routes import news_bp
from .health_routes import health_bp

__all__ = ['news_bp', 'health_bp']
