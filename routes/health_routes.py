"""시스템 상태 및 메트릭스 관련 라우트"""
from flask import Blueprint, jsonify
from datetime import datetime
from services.stock_service import stock_cache
from utils.metrics import metrics, get_cache_hit_ratio, get_avg_response_times
from config import Config

health_bp = Blueprint('health', __name__)


@health_bp.route('/api/health')
def health_check():
    """헬스체크 및 시스템 상태 확인"""
    # 캐시 정리
    expired_count = stock_cache.clear_expired()
    
    # 평균 응답 시간 계산
    avg_response_times = get_avg_response_times()
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache": {
            "size": stock_cache.size(),
            "max_size": Config.STOCK_CACHE_SIZE,
            "hits": metrics['cache_hits'],
            "misses": metrics['cache_misses'],
            "hit_ratio": get_cache_hit_ratio(),
            "expired_cleaned": expired_count
        },
        "performance": {
            "request_counts": dict(metrics['request_count']),
            "avg_response_times": avg_response_times,
            "error_counts": dict(metrics['errors'])
        },
        "config": {
            "environment": Config.ENVIRONMENT,
            "max_workers": Config.MAX_WORKERS,
            "cache_duration": Config.CACHE_DURATION
        }
    }
    
    return jsonify(health_data)


@health_bp.route('/api/metrics')
def get_metrics():
    """상세 메트릭스 정보"""
    return jsonify({
        "cache_metrics": {
            "hits": metrics['cache_hits'],
            "misses": metrics['cache_misses'],
            "size": stock_cache.size()
        },
        "request_metrics": dict(metrics['request_count']),
        "error_metrics": dict(metrics['errors']),
        "response_times": {k: {
            "count": len(v),
            "avg": sum(v) / len(v) if v else 0,
            "min": min(v) if v else 0,
            "max": max(v) if v else 0
        } for k, v in metrics['response_times'].items()}
    })
