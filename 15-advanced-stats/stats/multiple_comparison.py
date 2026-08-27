

def bonferroni_correct(p_values: list[float], alpha: float = 0.05) -> dict:
    corrected_alpha = alpha / len(p_values)

    significant = [p < corrected_alpha for p in p_values]

    return {
        "corrected_alpha": corrected_alpha,
        "significant": significant,
        "original_p_values": p_values
    }

if __name__ == "__main__":
    p_values = [0.01, 0.03, 0.04]
    result = bonferroni_correct(p_values)
    print(result)