import pytest
import numpy as np
from statistical_evaluator import StatisticalEvaluator

@pytest.fixture
def evaluator():
    return StatisticalEvaluator()

def test_compare_prompts_significant(evaluator):
    a = [0.5] * 50
    b = [0.8] * 50
    result = evaluator.compare_prompts(a, b)

    assert result['significant'] == True
    assert  result['p_value'] < 0.05
    assert result['mean_b'] > result['mean_a']

def test_compare_prompts_not_significant(evaluator):
    a = np.random.normal(0.75, 0.005, 50).tolist()
    b = np.random.normal(0.76, 0.005, 50).tolist()
    result = evaluator.compare_prompts(a, b)

    assert "p_value" in result
    assert "significant" in result
    assert isinstance(result["significant"], bool)

def test_confidence_interval_contains_mean(evaluator):
    scores = [0.7, 0.8, 0.75, 0.85, 0.78] * 10
    lower, upper = evaluator.confidence_interval(scores)
    mean = np.mean(scores)

    assert lower < mean < upper


def test_required_sample_size_reasonable(evaluator):
    n = evaluator.required_sample_size(effect_size=0.5)

    assert 30 < n < 200
    assert isinstance(n, int)


def test_plot_comparison_no_crash(evaluator):
    import matplotlib
    matplotlib.use('Agg')  # backend без GUI

    scores_a = [0.7, 0.8, 0.75] * 10
    scores_b = [0.8, 0.85, 0.82] * 10

    evaluator.plot_comparison(scores_a, scores_b)