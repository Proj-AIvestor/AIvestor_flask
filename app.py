# app.py (백엔드 서버 파일)
from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import requests
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 프론트엔드(React) 개발 서버(예: http://localhost:3000)에서의 요청을 허용합니다.
CORS(app)

def get_stock_data(ticker):
    """주어진 티커에 대한 주식 데이터를 가져옵니다."""
    try:
        # 티커 정제
        cleaned_ticker = ticker.replace('.N', '').replace('.O', '')
        if cleaned_ticker == '2222.SE':
            cleaned_ticker = '2222.SR'

        stock = yf.Ticker(cleaned_ticker)
        info = stock.info
        
        price = info.get('regularMarketPrice', info.get('currentPrice'))
        prev_close = info.get('previousClose')

        if price is None or prev_close is None:
            return {"error": "Could not fetch data"}

        change = price - prev_close
        change_percent = (change / prev_close) * 100
        
        return {
            "price": f"{price:.2f}",
            "change": f"{change:+.2f}",
            "changePercent": f"{change_percent:+.2f}",
            "isPositive": change >= 0
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_from_backend(endpoint, params):
    """백엔드 API로부터 데이터를 가져옵니다."""
    backend_url = f"{app.config['BACKEND_URL']}{endpoint}"
    try:
        response = requests.get(backend_url, params=params)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, {"error": f"Failed to fetch news from backend: {e}"}

def enrich_articles_with_stock_info(articles):
    """기사 목록에 주식 정보를 추가합니다."""
    processed_articles = []
    for article in articles:
        companies = article.get('companies', [])
        companies_info = {}
        for company_ticker in companies:
            companies_info[company_ticker] = get_stock_data(company_ticker)
        article['companiesInfo'] = companies_info
        processed_articles.append(article)
    return processed_articles

@app.route('/api/stock-info')
def get_stock_info():
    tickers_str = request.args.get('tickers')
    if not tickers_str:
        return jsonify({"error": "No tickers provided"}), 400

    tickers = tickers_str.split(',')
    response_data = {ticker: get_stock_data(ticker) for ticker in tickers}
    
    return jsonify(response_data)

@app.route('/api/news-with-stock')
def get_news_with_stock_info():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400

    news_data, error = fetch_from_backend('/api/news/top', {'date': date})
    if error:
        return jsonify(error), 500

    if news_data:
        processed_news_data = {}
        for category, articles in news_data.items():
            processed_news_data[category] = enrich_articles_with_stock_info(articles)
        return jsonify(processed_news_data)
    
    return jsonify({"error": "No news data available"}), 500

@app.route('/api/news-by-topic-with-stock')
def get_news_by_topic_with_stock_info():
    topic = request.args.get('topic')
    if not topic:
        return jsonify({"error": "Topic parameter is required"}), 400

    articles, error = fetch_from_backend('/api/news/list', {'topic': topic})
    if error:
        return jsonify(error), 500

    if articles:
        processed_news_data = {topic: enrich_articles_with_stock_info(articles)}
        return jsonify(processed_news_data)

    return jsonify({"error": "No articles available for this topic"}), 500

@app.route('/api/news-content-with-stock')
def get_news_content_with_stock_info():
    newsId = request.args.get('newsId')
    if not newsId:
        return jsonify({"error": "newsId parameter is required"}), 400
    
    article, error = fetch_from_backend('/api/news/detail', {'newsId': newsId})
    if error:
        return jsonify(error), 500
    
    if article:
        companies = article.get('companies', [])
        companies_info = {ticker: get_stock_data(ticker) for ticker in companies}
        article['companiesInfo'] = companies_info
        return jsonify(article)

    return jsonify({"error": "Article not found"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)