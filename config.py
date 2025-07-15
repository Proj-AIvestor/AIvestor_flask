import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

class Config:
    """Flask 앱의 설정 값을 담는 클래스"""
    BACKEND_URL = os.getenv('BACKEND_URL')
