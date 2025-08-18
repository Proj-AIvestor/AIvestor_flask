"""Flask 애플리케이션 메인 파일"""
from flask import Flask, jsonify
from flask_cors import CORS
import logging
import atexit
from config import Config
from routes import news_bp, health_bp
from services import cleanup_resources

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def create_app():
    """Flask 앱을 생성하고 설정합니다."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS 설정 - 프론트엔드(React) 개발 서버에서의 요청을 허용
    CORS(app)
    
    # Config 검증
    Config.validate_config()
    
    # Blueprint 등록
    app.register_blueprint(news_bp)
    app.register_blueprint(health_bp)
    
    # 에러 핸들러 등록
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {str(error)}")
        return jsonify({"error": "Internal server error"}), 500
    
    # 종료 시 리소스 정리
    atexit.register(cleanup_resources)
    
    logger.info(f"Flask app created in {Config.ENVIRONMENT} mode")
    logger.info(f"Cache settings: size={Config.STOCK_CACHE_SIZE}, duration={Config.CACHE_DURATION}s")
    logger.info(f"Thread pool: max_workers={Config.MAX_WORKERS}")
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG, port=5000)
