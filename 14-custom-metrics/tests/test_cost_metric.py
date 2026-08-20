from metrics.cost_metric import CostMetric

def test_cost_metric_positive():
    m = CostMetric()
    result = m.measure("any", "any", 0, 0.004)
    assert result.passed is True
    assert result.score == 1

def test_cost_metric_negative():
    m = CostMetric()
    result = m.measure("any", "any", 0, 0.02)
    assert result.passed is False
    assert result.score == 0