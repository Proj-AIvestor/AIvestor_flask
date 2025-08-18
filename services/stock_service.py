"""주식 데이터 관련 서비스"""
import yfinance as yf
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import Config
from utils.validators import validate_ticker, validate_stock_data
from utils.decorators import retry_with_backoff
from utils.cache import LimitedCache

logger = logging.getLogger(__name__)

# 캐시 인스턴스 생성
stock_cache = LimitedCache(
    max_size=Config.STOCK_CACHE_SIZE, 
    cache_duration=Config.CACHE_DURATION
)

# 스레드 풀 생성
executor = ThreadPoolExecutor(max_workers=Config.MAX_WORKERS)


@retry_with_backoff()
def get_stock_data(ticker):
    """주어진 티커에 대한 주식 데이터를 가져옵니다."""
    if not validate_ticker(ticker):
        logger.warning(f"Invalid ticker format: {ticker}")
        return ticker, {"error": "Invalid ticker format"}
    
    # 캐시 확인
    cached_result = stock_cache.get(ticker)
    if cached_result is not None:
        logger.debug(f"Cache hit for ticker: {ticker}")
        return cached_result
    
    try:
        logger.debug(f"Fetching stock data for: {ticker}")
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not validate_stock_data(info):
            result = (ticker, {"error": "Invalid or incomplete stock data"})
        else:
            company_name = info.get('shortName', info.get('longName', ticker))
            
            price = info.get('regularMarketPrice', info.get('currentPrice'))
            prev_close = info.get('previousClose')
            
            change = price - prev_close
            change_percent = (change / prev_close) * 100
            
            result = (company_name, {
                "price": f"{price:.2f}",
                "change": f"{change:+.2f}",
                "changePercent": f"{change_percent:+.2f}",
                "isPositive": change >= 0,
                "ticker": ticker,
                "lastUpdated": datetime.now().isoformat()
            })
        
        # 캐시에 저장
        stock_cache.set(ticker, result)
        logger.info(f"Successfully fetched and cached data for {ticker}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to fetch stock data for {ticker}: {str(e)}"
        logger.error(error_msg)
        result = (ticker, {"error": str(e)})
        # 에러도 짧은 시간 캐시 (중복 요청 방지)
        stock_cache.set(ticker, result)
        return result


def get_stock_data_batch(tickers):
    """여러 티커의 주식 데이터를 병렬로 가져옵니다."""
    if not tickers:
        return [], {}, {}
    
    # 유효한 티커만 필터링
    valid_tickers = [ticker for ticker in tickers if validate_ticker(ticker)]
    if not valid_tickers:
        logger.warning("No valid tickers provided")
        return [], {}, {}
    
    logger.info(f"Fetching stock data for {len(valid_tickers)} tickers")
    
    companies_info = {}
    companies_name = []
    ticker_to_name = {}
    
    # 병렬로 주식 데이터 가져오기
    future_to_ticker = {
        executor.submit(get_stock_data, ticker): ticker 
        for ticker in valid_tickers
    }
    
    for future in as_completed(future_to_ticker):
        ticker = future_to_ticker[future]
        try:
            company_name, stock_data = future.result(timeout=Config.REQUEST_TIMEOUT)
            companies_info[company_name] = stock_data
            companies_name.append(company_name)
            ticker_to_name[ticker] = company_name
        except Exception as exc:
            error_msg = f'{ticker} generated an exception: {exc}'
            logger.error(error_msg)
            companies_info[ticker] = {"error": str(exc)}
            companies_name.append(ticker)
            ticker_to_name[ticker] = ticker
    
    logger.info(f"Successfully processed {len(companies_info)} tickers")
    return companies_name, companies_info, ticker_to_name


def getName_StockInfo(article):
    """단일 기사에 주식 정보를 추가합니다."""
    if not article or not isinstance(article, dict):
        logger.warning("Invalid article data provided")
        return article
    
    companies_ticker = article.get('companies', [])
    if not companies_ticker:
        return article
    
    companies_name, companies_info, _ = get_stock_data_batch(companies_ticker)
    
    article['companiesInfo'] = companies_info
    article['companies'] = companies_name
    article['stockDataUpdated'] = datetime.now().isoformat()
    return article


def enrich_articles_with_stock_info(articles, key_type='name'):
    """기사 목록에 주식 정보를 추가합니다."""
    if not articles or not isinstance(articles, list):
        logger.warning("Invalid articles data provided")
        return []
    
    # 모든 기사에서 unique ticker 수집
    all_tickers = set()
    for article in articles:
        if isinstance(article, dict):
            all_tickers.update(article.get('companies', []))
    
    if not all_tickers:
        logger.info("No tickers found in articles")
        return articles
    
    logger.info(f"Processing {len(articles)} articles with {len(all_tickers)} unique tickers")
    
    # 모든 ticker에 대해 한 번에 데이터 가져오기
    _, companies_info_map, ticker_to_name = get_stock_data_batch(list(all_tickers))
    
    # 각 기사에 정보 매핑
    processed_articles = []
    for article in articles:
        if not isinstance(article, dict):
            processed_articles.append(article)
            continue
            
        companies_ticker = article.get('companies', [])
        article_companies_list = []
        article_companies_info = {}
        
        for ticker in companies_ticker:
            company_name = ticker_to_name.get(ticker, ticker)
            
            # key_type에 따라 이름 또는 티커를 리스트에 추가
            if key_type == 'ticker':
                article_companies_list.append(ticker)
            else: # 기본값은 'name'
                article_companies_list.append(company_name)

            if company_name in companies_info_map:
                article_companies_info[company_name] = companies_info_map[company_name]
        
        article['companies'] = article_companies_list
        article['companiesInfo'] = article_companies_info
        article['stockDataUpdated'] = datetime.now().isoformat()
        processed_articles.append(article)
    
    logger.info(f"Successfully enriched {len(processed_articles)} articles")
    return processed_articles


def cleanup_resources():
    """리소스 정리"""
    logger.info("Shutting down executor...")
    executor.shutdown(wait=True)
    logger.info("Resources cleaned up successfully")
