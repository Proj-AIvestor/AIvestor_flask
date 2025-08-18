"""뉴스 관련 라우트"""
from flask import Blueprint, jsonify, request
from services.news_service import fetch_from_backend
from services.stock_service import get_stock_data, enrich_articles_with_stock_info, getName_StockInfo
from utils.validators import validate_date_format
from utils.decorators import track_performance

news_bp = Blueprint('news', __name__)

@news_bp.route('/api/company-stockInfo')
@track_performance('company-stockInfo')
def get_company_stock_info():
    ticker = request.args.get('company')
    
    if not ticker:
        return jsonify({"error": "Missing 'company' query parameter"}), 400
    
    companies_name, company_stock_data = get_stock_data(ticker)
    
    if 'error' in company_stock_data:
        error_message = company_stock_data['error']
        
        if "Invalid ticker format" in error_message:
            return jsonify({"error": error_message, "ticker": companies_name}), 400
        elif "No stock data available" in error_message:
            return jsonify({"error": error_message, "ticker": companies_name}), 404
        
        else:
            return jsonify({"error": "Internal server error", "details": error_message, "ticker": companies_name}), 500
        
    response_data = {
        **company_stock_data  # company_stock_data 딕셔너리의 내용을 펼침
    }
    
    return jsonify(response_data)

@news_bp.route('/api/news-with-stock')
@track_performance('news-with-stock')
def get_news_with_stock_info():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    
    if not validate_date_format(date):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    news_data, error = fetch_from_backend('/api/news/top', {'date': date})
    if error:
        return jsonify(error), 500

    if news_data:
        processed_news_data = {}
        for category, articles in news_data.items():
            processed_news_data[category] = enrich_articles_with_stock_info(articles)
        
        return jsonify(processed_news_data)
    
    return jsonify({"error": "No news data available"}), 500


@news_bp.route('/api/news-by-topic-with-stock')
@track_performance('news-by-topic-with-stock')
def get_news_by_topic_with_stock_info():
    topic = request.args.get('topic')
    if not topic or len(topic.strip()) == 0:
        return jsonify({"error": "Topic parameter is required"}), 400

    articles, error = fetch_from_backend('/api/news/list', {'topic': topic})
    if error:
        return jsonify(error), 500

    if articles:
        processed_news_data = {topic: enrich_articles_with_stock_info(articles)}
        return jsonify(processed_news_data)

    return jsonify({"error": "No articles available for this topic"}), 500


@news_bp.route('/api/news-content-with-stock')
@track_performance('news-content-with-stock')
def get_news_content_with_stock_info():
    newsId = request.args.get('newsId')
    if not newsId or len(newsId.strip()) == 0:
        return jsonify({"error": "newsId parameter is required"}), 400
    
    article, error = fetch_from_backend('/api/news/detail', {'newsId': newsId})
    if error:
        return jsonify(error), 500
    
    if article:
        processed_article = getName_StockInfo(article)
        return jsonify(processed_article)

    return jsonify({"error": "Article not found"}), 500


@news_bp.route('/api/date-news-with-stock')
@track_performance('date-news-with-stock')
def get_date_news_with_stock_info():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    
    if not validate_date_format(date):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    news_data, error = fetch_from_backend('/api/news/by-date', {'date': date})
    if error:
        return jsonify(error), 500

    if news_data:
        processed_news_data = {}
        for category, articles in news_data.items():
            processed_news_data[category] = enrich_articles_with_stock_info(articles)
        return jsonify(processed_news_data)
    
    return jsonify({"error": "No news data available"}), 500

@news_bp.route('/api/date-news-with-stock-ticker')
@track_performance('date-news-with-stock-ticker')
def get_date_news_with_stock_ticker_info():
    date = request.args.get('date')
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400
    
    if not validate_date_format(date):
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    news_data, error = fetch_from_backend('/api/news/by-date', {'date': date})
    if error:
        return jsonify(error), 500

    if news_data:
        processed_news_data = {}
        for category, articles in news_data.items():
            processed_news_data[category] = enrich_articles_with_stock_info(articles, key_type='ticker')
        return jsonify(processed_news_data)
    
    return jsonify({"error": "No news data available"}), 500