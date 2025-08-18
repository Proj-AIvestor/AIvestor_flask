"""간단한 테스트 스크립트"""
import requests
import json
from datetime import datetime, timedelta

# 테스트 설정
BASE_URL = "http://localhost:5000"

def test_health():
    """헬스체크 테스트"""
    print("=== Health Check Test ===")
    response = requests.get(f"{BASE_URL}/api/health")
    if response.status_code == 200:
        print("✓ Health check passed")
        print(json.dumps(response.json(), indent=2))
    else:
        print("✗ Health check failed")
        print(response.text)
    print()

def test_metrics():
    """메트릭스 테스트"""
    print("=== Metrics Test ===")
    response = requests.get(f"{BASE_URL}/api/metrics")
    if response.status_code == 200:
        print("✓ Metrics endpoint working")
        print(json.dumps(response.json(), indent=2))
    else:
        print("✗ Metrics endpoint failed")
        print(response.text)
    print()

def test_news_with_stock():
    """뉴스 + 주식 정보 테스트"""
    print("=== News with Stock Test ===")
    # 어제 날짜 사용
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    response = requests.get(f"{BASE_URL}/api/news-with-stock", params={'date': yesterday})
    if response.status_code == 200:
        print(f"✓ News with stock data for {yesterday} fetched successfully")
        data = response.json()
        # 첫 번째 카테고리의 첫 번째 기사만 출력
        for category, articles in data.items():
            if articles:
                print(f"\nCategory: {category}")
                print(f"First article: {articles[0].get('title', 'No title')}")
                if 'companiesInfo' in articles[0]:
                    print(f"Companies: {list(articles[0]['companiesInfo'].keys())}")
                break
    else:
        print("✗ News with stock fetch failed")
        print(response.text)
    print()

def test_invalid_request():
    """잘못된 요청 테스트"""
    print("=== Invalid Request Test ===")
    # 날짜 파라미터 없이 요청
    response = requests.get(f"{BASE_URL}/api/news-with-stock")
    if response.status_code == 400:
        print("✓ Invalid request properly handled")
        print(response.json())
    else:
        print("✗ Invalid request not handled properly")
        print(response.text)
    print()

if __name__ == "__main__":
    print("Starting API tests...\n")
    
    try:
        test_health()
        test_metrics()
        test_news_with_stock()
        test_invalid_request()
        
        print("All tests completed!")
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure the Flask app is running on port 5000.")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
