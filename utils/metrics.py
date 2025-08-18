from collections import defaultdict

# 성능 메트릭스
metrics = {
    'request_count': defaultdict(int),
    'response_times': defaultdict(list),
    'cache_hits': 0,
    'cache_misses': 0,
    'errors': defaultdict(int)
}


def increment_request_count(endpoint):
    """요청 카운트 증가"""
    metrics['request_count'][endpoint] += 1


def add_response_time(endpoint, response_time):
    """응답 시간 추가"""
    metrics['response_times'][endpoint].append(response_time)


def increment_error_count(endpoint):
    """에러 카운트 증가"""
    metrics['errors'][endpoint] += 1


def increment_cache_hit():
    """캐시 히트 증가"""
    metrics['cache_hits'] += 1


def increment_cache_miss():
    """캐시 미스 증가"""
    metrics['cache_misses'] += 1


def get_metrics():
    """메트릭스 반환"""
    return metrics


def get_cache_hit_ratio():
    """캐시 히트 비율 계산"""
    total = metrics['cache_hits'] + metrics['cache_misses']
    return metrics['cache_hits'] / total if total > 0 else 0


def get_avg_response_times():
    """평균 응답 시간 계산"""
    avg_response_times = {}
    for endpoint, times in metrics['response_times'].items():
        if times:
            avg_response_times[endpoint] = sum(times) / len(times)
    return avg_response_times