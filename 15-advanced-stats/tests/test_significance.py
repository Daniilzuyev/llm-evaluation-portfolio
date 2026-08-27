import pytest
from stats.significance import paired_ttest
from stats.significance import mann_whitney

scores_a = [0.8, 0.75, 0.9, 0.85, 0.7]
scores_b = [0.85, 0.8, 0.92, 0.88, 0.75]

scores_clearly_different_a = [0.1, 0.15, 0.2, 0.12, 0.18, 0.14, 0.16, 0.11]
scores_clearly_different_b = [0.8, 0.85, 0.9, 0.82, 0.88, 0.84, 0.86, 0.81]

scores_similar_a = [0.5, 0.55, 0.5, 0.52, 0.48, 0.51, 0.49, 0.53]
scores_similar_b = [0.52, 0.48, 0.51, 0.5, 0.55, 0.49, 0.53, 0.5]

def test_significance_positive():
    result = paired_ttest(scores_a, scores_b)
    assert result['significant'] == True
    assert result['p_value'] <= 0.05

def test_paired_ttest_raises_on_unequal_length():
    with pytest.raises(ValueError):
        paired_ttest([0.8, 0.9], [0.5])

def test_mann_whitney_detects_clear_difference():
    result = mann_whitney(scores_clearly_different_a, scores_clearly_different_b)
    assert result['significant'] == True

def test_mann_whitney_no_difference():
    result = mann_whitney(scores_similar_a, scores_similar_b)
    assert result['significant'] == False