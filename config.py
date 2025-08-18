import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

class Config:
    # 스프링부트 url 설정
    BACKEND_URL = os.getenv('BACKEND_URL')
    
    # 환경 설정
    ENVIRONMENT = os.getenv('FLASK_ENV', 'development')  # 추가: 실행 환경 (development/production)
    DEBUG = ENVIRONMENT == 'development'  # 추가: 디버그 모드 자동 설정
    
    # 캐시 관련 설정
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', 60))  # 추가: 캐시 유지 시간 (초)
    STOCK_CACHE_SIZE = int(os.getenv('STOCK_CACHE_SIZE', 1000))  # 추가: 캐시 최대 크기
    
    # 스레드 풀 설정
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 20))  # 추가: 최대 동시 작업 스레드 수
    
    # 타임아웃 설정
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 10))  # 추가: API 요청 타임아웃 (초)
    
    # 재시도 설정
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))  # 추가: 최대 재시도 횟수
    BACKOFF_FACTOR = float(os.getenv('BACKOFF_FACTOR', 0.5))  # 추가: 재시도 백오프 계수
    
    # 로깅 설정
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 추가: 로그 레벨 (DEBUG/INFO/WARNING/ERROR)
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 추가: 로그 포맷
    
    # 보안 설정
    # SECRET_KEY = os.getenv('SECRET_KEY')  # 추가: Flask 시크릿 키
    
    # yfinance API 관련 설정 (향후 확장을 위해)
    # STOCK_API_BASE_URL = os.getenv('STOCK_API_BASE_URL', '')  # 추가: 대체 주식 API URL (선택사항)
    # STOCK_API_KEY = os.getenv('STOCK_API_KEY', '')  # 추가: 주식 API 키 (선택사항)
    
    # 성능 모니터링 설정
    ENABLE_METRICS = os.getenv('ENABLE_METRICS', 'true').lower() == 'true'  # 추가: 메트릭스 수집 활성화
    METRICS_RETENTION_HOURS = int(os.getenv('METRICS_RETENTION_HOURS', 24))  # 추가: 메트릭스 보관 시간 (시간)
    
    @classmethod
    def validate_config(cls):
        """설정 값들의 유효성을 검증합니다."""  # 추가: 설정 검증 메서드
        required_vars = ['BACKEND_URL']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Required environment variables are missing: {', '.join(missing_vars)}")
        
        return True
