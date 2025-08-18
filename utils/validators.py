"""유효성 검증 유틸리티"""
from datetime import datetime


def validate_ticker(ticker):
    """티커 형식을 검증합니다."""
    if not ticker or not isinstance(ticker, str):
        return False
    if len(ticker) > 10 or len(ticker) < 1:
        return False
    # 기본적인 알파벳과 숫자, 점, 하이픈만 허용
    allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-')
    return all(c.upper() in allowed_chars for c in ticker)


def validate_date_format(date_str):
    """날짜 형식을 검증합니다 (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_stock_data(info):
    """주식 데이터 검증"""
    if not info or not isinstance(info, dict):
        return False, "데이터가 없거나 올바르지 않은 형식입니다"
    
    # 가격 검증
    price_fields = ['regularMarketPrice', 'currentPrice']
    current_price = None
    for field in price_fields:
        if field in info and info[field] is not None:
            current_price = info[field]
            break
    
    if current_price is None:
        return False, "현재 가격 정보가 없습니다"
    
    # 전일 종가 검증
    if 'previousClose' not in info or info['previousClose'] is None:
        return False, "전일 종가 정보가 없습니다"
    
    # 가격이 음수인지 검증
    if current_price <= 0 or info['previousClose'] <= 0:
        return False, "가격이 0 이하입니다"
    
    return True, "유효한 데이터"
