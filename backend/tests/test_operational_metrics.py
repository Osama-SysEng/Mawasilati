from app.core.metrics import RuntimeMetrics
from app.core.load_safety import assert_safe_target


def test_metrics_collect_bounded_route_stats():
    metrics = RuntimeMetrics()
    metrics.started()
    metrics.record('/api/v1/trip/book', 201, .02)
    metrics.record('/api/v1/trip/book', 500, .04)
    metrics.completed()
    result = metrics.snapshot()
    assert result['in_flight'] == 0
    assert result['routes']['/api/v1/trip/book']['requests'] == 2
    assert result['routes']['/api/v1/trip/book']['server_errors'] == 1


def test_load_probe_rejects_remote_without_explicit_opt_in():
    try:
        assert_safe_target('https://staging.example.test', False)
        assert False
    except ValueError:
        pass
