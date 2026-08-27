from report import compare_models


def test_compare_models_returns_all_metrics():
    metrics_data = {
        "accuracy": {"a": [0.8, 0.75, 0.9, 0.85, 0.7], "b": [0.85, 0.8, 0.92, 0.88, 0.75]},
        "latency": {"a": [1200, 1300, 1080, 1250, 1180], "b": [1150, 1250, 1050, 1150, 1100]},
    }
    result = compare_models(metrics_data)
    assert set(result["metrics"].keys()) == {"accuracy", "latency"}


def test_compare_models_corrected_alpha():
    metrics_data = {
        "accuracy": {"a": [0.8, 0.75, 0.9, 0.85, 0.7], "b": [0.85, 0.8, 0.92, 0.88, 0.75]},
        "latency": {"a": [1200, 1300, 1080, 1250, 1180], "b": [1150, 1250, 1050, 1150, 1100]},
    }
    result = compare_models(metrics_data)
    assert result["corrected_alpha"] == 0.025