from stats.significance import paired_ttest
from stats.effect_size import cohens_d
from stats.multiple_comparison import bonferroni_correct


def compare_models(metrics_data: dict) -> dict:
    results_by_metric = {}
    p_values = []

    # Часть 1: t-test + effect size для каждой метрики
    for metric_name, data in metrics_data.items():
        ttest_result = paired_ttest(data["a"], data["b"])
        effect_result = cohens_d(data["a"], data["b"])

        results_by_metric[metric_name] = {
            "statistic": ttest_result["statistic"],
            "p_value": ttest_result["p_value"],
            "cohens_d": effect_result["d"],
            "interpretation": effect_result["interpretation"],
        }
        p_values.append(ttest_result["p_value"])

    # Часть 2: bonferroni-коррекция across всех метрик
    correction = bonferroni_correct(p_values)

    # Часть 3: собрать финальный отчёт, заменив "сырую" значимость на скорректированную
    for i, metric_name in enumerate(results_by_metric):
        results_by_metric[metric_name]["significant_corrected"] = correction["significant"][i]

    return {
        "metrics": results_by_metric,
        "corrected_alpha": correction["corrected_alpha"],
    }


if __name__ == "__main__":
    metrics_data = {
        "accuracy": {"a": [0.8, 0.75, 0.9, 0.85, 0.7], "b": [0.85, 0.8, 0.92, 0.88, 0.75]},
        "latency": {"a": [1200, 1300, 1080, 1250, 1180], "b": [1150, 1250, 1050, 1150, 1100]},
    }
    print(compare_models(metrics_data))