from stats.effect_size import cohens_d

scores_a = [0.1, 0.15, 0.2, 0.12, 0.18, 0.14, 0.16, 0.11]
scores_b = [0.8, 0.85, 0.9, 0.82, 0.88, 0.84, 0.86, 0.81]

scores_similar_a = [0.5, 0.55, 0.5, 0.52, 0.48, 0.51, 0.49, 0.53]
scores_similar_b = [0.52, 0.48, 0.51, 0.5, 0.55, 0.49, 0.53, 0.5]

def test_cohens_d_large_effect():
    result = cohens_d(scores_a, scores_b)
    assert result["interpretation"] == "large"

def test_cohens_d_negligible_effect():
    result = cohens_d(scores_similar_a, scores_similar_b)
    assert result["interpretation"] == "negligible"