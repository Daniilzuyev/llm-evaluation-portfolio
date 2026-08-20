from metrics.latency_metric import LatencyMetric

def test_latency_metric():
    m = LatencyMetric()
    result = m.measure("any", "any", 1500)
    assert result.passed is True
    assert result.score == 1

def test_latency_metric_out_of_range():
    m = LatencyMetric()
    result = m.measure("any", "any", 2500)
    assert result.passed is False
    assert result.score == 0