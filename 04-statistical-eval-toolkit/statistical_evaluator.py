import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from statsmodels.stats.power import tt_ind_solve_power

class StatisticalEvaluator:

    def compare_prompts(self, results_a: list[float], results_b: list[float], test_type: str = "paired") -> dict:

        pooled_std = np.sqrt((np.std(results_a) ** 2 + np.std(results_b) ** 2) / 2)
        mean_a = np.mean(results_a)
        mean_b = np.mean(results_b)
        if test_type == "paired":
            p_value = stats.ttest_rel(results_a, results_b)[1]
        else:
            p_value = stats.ttest_ind(results_a, results_b)[1]


        return {
            "mean_a": mean_a,
            "mean_b": mean_b,
            "p_value": p_value,
            "significant": True if p_value < 0.05 else False,
            "effect_size": (mean_a - mean_b) / pooled_std,
        }

    def confidence_interval(self, data: list[float], confidence: float = 0.95) -> tuple[float, float]:

        mean = np.mean(data)
        sem = stats.sem(data)
        ci = stats.t.interval(
            confidence,
            len(data) - 1,
            loc=mean,
            scale = sem
        )

        return ci

    def required_sample_size(self, effect_size: float = 0.5, alpha: float = 0.05,
                             power: float = 0.8) -> int:
        n = tt_ind_solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power
        )

        return int(np.ceil(n))

    def plot_comparison(self, scores_a: list[float], scores_b: list[float],
                        labels: tuple[str, str] = ("Prompt A", "Prompt B")):

        plt.figure(figsize=(10, 6))
        plt.boxplot([scores_a, scores_b], labels=labels)
        plt.title("Prompt Comparison", fontsize=14, fontweight="bold")
        plt.ylabel("Score", fontsize=12)
        plt.grid(axis="y", alpha=0.3)

        mean_a = np.mean(scores_a)
        mean_b = np.mean(scores_b)
        ci_a = self.confidence_interval(scores_a)
        ci_b = self.confidence_interval(scores_b)

        # Error bars
        positions = [1, 2]
        means = [mean_a, mean_b]
        errors = [
            [mean_a - ci_a[0], mean_b - ci_b[0]],
            [ci_a[1] - mean_a, ci_b[1] - mean_b]
        ]

        plt.errorbar(positions, means, yerr=errors,
                     fmt='o', color='red', markersize=8,
                     capsize=10, capthick=2, label='Mean with 95% CI')

        plt.legend()
        plt.tight_layout()  # ← переместил сюда
        plt.show()