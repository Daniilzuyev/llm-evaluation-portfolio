import numpy as np


def bootstrap_ci(scores: list[float], n_resamples: int = 10000, confidence_level: float = 0.95) -> dict:
    rng = np.random.default_rng()
    scores = np.array(scores)

    means = []
    for _ in range(n_resamples):
        resample = rng.choice(scores, size=len(scores), replace=True)
        mean = np.mean(resample)
        means.append(mean)

    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = 100 - (alpha / 2) * 100

    ci_lower = np.percentile(means, lower_percentile)
    ci_upper = np.percentile(means, upper_percentile)

    return {
        "mean": np.mean(scores),
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "confidence_level": confidence_level
    }


if __name__ == "__main__":
    scores = [0.8, 0.75, 0.9, 0.7]
    result = bootstrap_ci(scores)
    print(result)