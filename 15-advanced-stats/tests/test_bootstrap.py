import pytest
from stats.bootstrap import bootstrap_ci

scores = [0.8, 0.75, 0.9, 0.85, 0.7]

def test_bootstrap_ci_contains_mean():
    result = bootstrap_ci(scores)
    assert result["ci_lower"] <= result["mean"] <= result["ci_upper"]

def test_bootstrap_ci_lower_less_than_upper():
    result = bootstrap_ci(scores)
    assert result["ci_lower"] < result["ci_upper"]