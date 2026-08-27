from stats.power import required_sample_size

def test_required_sample_size_decreases_with_larger_effect():
    result_a = required_sample_size(effect_size=0.8)
    result_b = required_sample_size(effect_size=0.2)
    assert result_a["required_n_per_group"] < result_b["required_n_per_group"]

def test_required_sample_size_returns_integer():
    result = required_sample_size(effect_size=0.5)
    assert isinstance(result["required_n_per_group"], int)