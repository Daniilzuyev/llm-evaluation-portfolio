from stats.multiple_comparison import bonferroni_correct


def test_bonferroni_correct_reduces_significant_count():
    p_values = [0.01, 0.03, 0.04]
    result = bonferroni_correct(p_values)
    assert result["significant"] == [True, False, False]

def test_bonferroni_correct_alpha_calculation():
    p_values = [0.01, 0.03, 0.04, 0.07]
    result = bonferroni_correct(p_values)
    assert result["corrected_alpha"] == 0.0125