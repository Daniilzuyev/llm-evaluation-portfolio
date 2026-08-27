import scipy.stats

# scores_a = [0.8, 0.75, 0.9, 0.85, 0.7]
# scores_b = [0.85, 0.8, 0.92, 0.88, 0.75]

def paired_ttest(scores_a: list[float], scores_b: list[float]) -> dict:
    if len(scores_a) != len(scores_b):
        raise ValueError("Both arrays must have the same length")
    result = scipy.stats.ttest_rel(scores_a, scores_b)
    return {
        "statistic": result.statistic,
        "p_value": result.pvalue,
        "significant": result.pvalue < 0.05
    }

def mann_whitney(scores_a: list[float], scores_b: list[float]) -> dict:
    result = scipy.stats.mannwhitneyu(scores_a, scores_b)
    return {
        "statistic": result.statistic,
        "p_value": result.pvalue,
        "significant": result.pvalue < 0.05
    }

if __name__ == "__main__":
    scores_a = [0.8, 0.75, 0.9, 0.85, 0.7]
    scores_b = [0.85, 0.8, 0.92, 0.88, 0.75]
    scores_c = [0.1, 0.15, 0.2]
    scores_d = [0.8, 0.85, 0.9]
    scores_clearly_different_a = [0.1, 0.15, 0.2, 0.12, 0.18, 0.14, 0.16, 0.11]
    scores_clearly_different_b = [0.8, 0.85, 0.9, 0.82, 0.88, 0.84, 0.86, 0.81]

    scores_similar_a = [0.5, 0.55, 0.5, 0.52, 0.48, 0.51, 0.49, 0.53]
    scores_similar_b = [0.52, 0.48, 0.51, 0.5, 0.55, 0.49, 0.53, 0.5]

    # print(paired_ttest(scores_a, scores_b))
    print(mann_whitney(scores_clearly_different_a, scores_clearly_different_b))
    print('-----------')
    print(mann_whitney(scores_similar_a, scores_similar_b))

    try:
        paired_ttest([0.8, 0.9], [0.5])
    except ValueError as e:
        print("Ok, caught error:", e)

