import numpy as np

def cohens_d(scores_a: list[float], scores_b: list[float]) -> dict:
    scores_a = np.array(scores_a)
    scores_b = np.array(scores_b)
    avg_score_a = np.mean(scores_a)
    avg_score_b = np.mean(scores_b)
    std_score_a = np.std(scores_a, ddof=1)
    std_score_b = np.std(scores_b, ddof=1)

    n_a = len(scores_a)
    n_b = len(scores_b)
    pooled_std = np.sqrt(
        ((n_a - 1) * std_score_a ** 2 + (n_b - 1) * std_score_b ** 2) / (n_a + n_b - 2)
    )

    d = (avg_score_a - avg_score_b) / pooled_std

    if abs(d) < 0.2:
        interpretation = "negligible"
    elif abs(d) < 0.5:
        interpretation = "small"
    elif abs(d) < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    return {
        "d": d,
        "interpretation": interpretation
    }

if __name__ == "__main__":
    scores_a = [0.1, 0.15, 0.2, 0.12, 0.18, 0.14, 0.16, 0.11]
    scores_b = [0.8, 0.85, 0.9, 0.82, 0.88, 0.84, 0.86, 0.81]
    print(cohens_d(scores_a, scores_b))

    scores_similar_a = [0.5, 0.55, 0.5, 0.52, 0.48, 0.51, 0.49, 0.53]
    scores_similar_b = [0.52, 0.48, 0.51, 0.5, 0.55, 0.49, 0.53, 0.5]
    print(cohens_d(scores_similar_a, scores_similar_b))