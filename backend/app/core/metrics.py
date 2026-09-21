from collections import Counter, defaultdict
from threading import Lock


class RuntimeMetrics:
    def __init__(self):
        self._lock = Lock()
        self._requests = Counter()
        self._errors = Counter()
        self._latency = defaultdict(float)
        self._in_flight = 0

    def started(self):
        with self._lock:
            self._in_flight += 1

    def completed(self):
        with self._lock:
            self._in_flight = max(0, self._in_flight - 1)

    def record(self, route: str, status: int, seconds: float):
        route = route[:160]
        with self._lock:
            self._requests[route] += 1
            self._latency[route] += seconds
            if status >= 500:
                self._errors[route] += 1

    def snapshot(self) -> dict:
        with self._lock:
            return {
                'in_flight': self._in_flight,
                'routes': {
                    route: {'requests': count, 'server_errors': self._errors[route], 'avg_latency_ms': round(self._latency[route] * 1000 / count, 2)}
                    for route, count in self._requests.items()
                },
            }


runtime_metrics = RuntimeMetrics()
