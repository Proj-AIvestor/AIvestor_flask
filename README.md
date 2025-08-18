# AIvestor Flask Backend

AI 기반 투자 뉴스 분석 서비스의 Flask 백엔드입니다.

## 프로젝트 구조

```
AIvestor_flask/
│
├── app.py                # Flask 애플리케이션 메인 파일
├── config.py             # 설정 관리 파일
├── .env                  # 환경 변수 파일
├── requirements.txt      # 프로젝트 의존성
│
├── routes/               # API 라우트 모듈
│   ├── __init__.py
│   ├── news_routes.py    # 뉴스 관련 엔드포인트
│   └── health_routes.py  # 헬스체크 및 메트릭스 엔드포인트
│
├── services/             # 비즈니스 로직 서비스
│   ├── __init__.py
│   ├── stock_service.py  # 주식 데이터 처리 서비스
│   └── news_service.py   # 뉴스 데이터 처리 서비스
│
└── utils/                # 유틸리티 모듈
    ├── __init__.py
    ├── cache.py          # LRU 캐시 구현
    ├── decorators.py     # 데코레이터 (재시도, 성능 추적)
    ├── metrics.py        # 성능 메트릭스 관리
    └── validators.py     # 입력 검증 함수
```

## 모듈별 설명

### app.py
- Flask 앱 생성 및 설정
- Blueprint 등록
- 에러 핸들러 설정
- 앱 실행 엔트리포인트

### routes/
- **news_routes.py**: 뉴스 + 주식 정보 API 엔드포인트
  - `/api/news-with-stock`: 날짜별 주요 뉴스
  - `/api/news-by-topic-with-stock`: 주제별 뉴스
  - `/api/news-content-with-stock`: 뉴스 상세 내용
  - `/api/date-news-with-stock`: 특정 날짜 뉴스
- **health_routes.py**: 시스템 상태 관련 엔드포인트
  - `/api/health`: 헬스체크 및 시스템 상태
  - `/api/metrics`: 상세 메트릭스 정보

### services/
- **stock_service.py**: 주식 데이터 처리
  - yfinance를 통한 주식 정보 조회
  - 병렬 처리로 성능 최적화
  - 뉴스에 주식 정보 추가
- **news_service.py**: 백엔드 API 통신
  - 뉴스 데이터 페치

### utils/
- **cache.py**: LRU 캐시 구현으로 API 호출 최적화
- **decorators.py**: 재시도 로직, 성능 추적 데코레이터
- **metrics.py**: 성능 메트릭스 수집 및 관리
- **validators.py**: 입력값 검증 함수

## 환경 변수

- `BACKEND_URL`: 백엔드 API URL
- `FLASK_ENV`: 실행 환경 (development/production)
- `CACHE_DURATION`: 캐시 유지 시간 (초)
- `STOCK_CACHE_SIZE`: 캐시 최대 크기
- `MAX_WORKERS`: 스레드 풀 워커 수
- 기타 설정은 `.env` 파일 참조

## 주요 기능

1. **뉴스 데이터 처리**: 백엔드 API에서 뉴스 가져오기
2. **주식 정보 추가**: yfinance를 통해 실시간 주식 정보 추가
3. **캐싱**: LRU 캐시로 중복 API 호출 방지
4. **병렬 처리**: 다중 주식 정보를 동시에 처리
5. **성능 모니터링**: 요청 수, 응답 시간, 캐시 히트율 등 추적
6. **에러 처리**: 재시도 로직 및 graceful 에러 핸들링
