"""캐시 관련 유틸리티"""
import threading
import time
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class LimitedCache:
    """LRU 캐시 구현 - 메모리 누수 방지"""
    def __init__(self, max_size=1000, cache_duration=60):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.cache_duration = cache_duration
        self.lock = threading.Lock()
    
    def get(self, key):
        from utils.metrics import metrics
        
        with self.lock:
            if key in self.cache:
                data, timestamp = self.cache[key]
                if time.time() - timestamp < self.cache_duration:
                    # LRU: 최근 사용한 항목을 맨 뒤로
                    self.cache.move_to_end(key)
                    metrics['cache_hits'] += 1
                    return data
                else:
                    # 만료된 캐시 제거
                    del self.cache[key]
        
        metrics['cache_misses'] += 1
        return None
    
    def set(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.max_size:
                # 가장 오래된 항목 제거
                self.cache.popitem(last=False)
            
            self.cache[key] = (value, time.time())
    
    def size(self):
        with self.lock:
            return len(self.cache)
    
    def clear_expired(self):
        """만료된 캐시 항목들을 정리합니다."""
        with self.lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, timestamp) in self.cache.items() 
                if current_time - timestamp > self.cache_duration
            ]
            for key in expired_keys:
                del self.cache[key]
            return len(expired_keys)
