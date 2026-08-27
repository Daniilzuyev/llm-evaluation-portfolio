# 15-advanced-stats

Advanced statistical toolkit for comparing LLM eval scores across prompt/model variants — significance testing, effect size, bootstrap confidence intervals, sample size planning, and multiple-comparison correction.

Built as Topic 20 of a self-paced LLM Evaluation Engineer curriculum ([full curriculum](../llm-eval-curriculum.md)).

## Problem this solves

`04-stats-for-eval` (T10) covered the basics: a t-test and a confidence interval. That toolkit breaks down in three common eval situations:

1. **Eval scores are often not normally distributed.** LLM-as-judge scores are frequently skewed, bounded to [0, 1], or near-binary. A standard t-test assumes normality — violate it and the p-value becomes unreliable.
2. **"Statistically significant" is not the same as "practically meaningful."** With enough test cases, even a trivial improvement can produce p < 0.05. A p-value alone never says *how big* the difference is.
3. **Comparing several metrics at once inflates false positives.** Checking accuracy, latency, and cost separately, each at α = 0.05, raises the chance that at least one shows "significance" purely by chance.

This module adds the tools eval work actually needs to defend a "prompt B is better than prompt A" claim, not just assert it.

## Module structure

```
15-advanced-stats/
├── stats/
│   ├── significance.py         # paired_ttest(), mann_whitney()
│   ├── effect_size.py          # cohens_d()
│   ├── bootstrap.py            # bootstrap_ci()
│   ├── power.py                # required_sample_size()
│   └── multiple_comparison.py  # bonferroni_correct()
├── report.py                    # compare_models() — ties all 5 modules together
├── tests/                       # 14 pytest tests, 2+ per module
└── README.md
```

## What each module does

### `significance.py` — is the difference real, or noise?

**`paired_ttest(scores_a, scores_b)`**
For the *same* test cases scored under two conditions (e.g. prompt v1 vs v2, same 30 texts). Pairing removes per-test-case variance and gives more statistical power with fewer samples — important when eval sets are typically 30–50 cases, not 500. Requires `len(scores_a) == len(scores_b)`; raises `ValueError` otherwise.

**`mann_whitney(scores_a, scores_b)`**
For *independent* groups (different, non-overlapping test cases — e.g. 20 red-team prompts run only against GPT-4, 20 different ones run only against Claude), or when the same paired data is too skewed/binary for the t-test's normality assumption to hold. Ranks values instead of using raw magnitudes, so it makes no distributional assumption. Trade-off: on small samples (n≈3–5) it has much lower power than the paired t-test and can miss a real effect purely from lack of data — a limitation of the method, not a bug.

Both return: `{"statistic": float, "p_value": float, "significant": bool}` (α = 0.05).

### `effect_size.py` — how big is the difference?

**`cohens_d(scores_a, scores_b)`**
A p-value says whether a difference exists; it says nothing about its size. Cohen's d standardizes the difference in means by the pooled standard deviation, giving a sample-size-independent measure of magnitude.

```
d = (mean_a - mean_b) / pooled_std
pooled_std = sqrt( ((n_a-1)*std_a² + (n_b-1)*std_b²) / (n_a+n_b-2) )
```

Interpretation thresholds (Cohen, 1988), applied to `abs(d)`:

| `abs(d)` | Interpretation |
|---|---|
| < 0.2 | negligible |
| 0.2 – 0.5 | small |
| 0.5 – 0.8 | medium |
| ≥ 0.8 | large |

Returns: `{"d": float, "interpretation": str}`.

### `bootstrap.py` — a distribution-free confidence interval

**`bootstrap_ci(scores, n_resamples=10000, confidence_level=0.95)`**
Resamples the original data *with replacement* `n_resamples` times, computes the mean of each resample, and takes the percentile range of that distribution as the CI. No normality assumption required — more robust than a classical CI on skewed eval scores.

Returns: `{"mean": float, "ci_lower": float, "ci_upper": float, "confidence_level": float}`.

### `power.py` — how many test cases do I actually need?

**`required_sample_size(effect_size, alpha=0.05, power=0.8)`**
Uses `statsmodels.stats.power.TTestIndPower` to answer: given an expected effect size, how many test cases per group are needed to reliably detect it? Result is rounded **up** (`math.ceil`) — a fractional requirement means the smaller integer is insufficient.

Empirical result from this module (α=0.05, power=0.8):

| Effect size (d) | Required n per group |
|---|---|
| 0.2 (small) | 394 |
| 0.5 (medium) | 64 |
| 0.8 (large) | 26 |

**Practical takeaway:** typical eval sets in this portfolio run 30–50 test cases. That's enough to reliably detect medium-to-large effects, but a small (d≈0.2) improvement — the kind a minor prompt tweak often produces — is statistically undetectable at that sample size. This is worth stating explicitly before claiming a small prompt change is validated.

Returns: `{"required_n_per_group": int, "effect_size": float, "alpha": float, "power": float}`.

### `multiple_comparison.py` — correcting for testing several metrics at once

**`bonferroni_correct(p_values, alpha=0.05)`**
Running a separate significance test per metric (accuracy, latency, cost — as in `14-custom-metrics`) inflates the chance that at least one shows a false positive. Bonferroni correction tightens the threshold by dividing it by the number of comparisons: `corrected_alpha = alpha / len(p_values)`. Each p-value is then checked against this stricter threshold instead of the original 0.05.

Returns: `{"corrected_alpha": float, "significant": list[bool], "original_p_values": list[float]}`.

### `report.py` — putting it together

**`compare_models(metrics_data: dict) -> dict`**
The function a CI/CD eval gate would actually call. Input is a dict of metrics, each holding paired score arrays:

```python
metrics_data = {
    "accuracy": {"a": [...], "b": [...]},
    "latency":  {"a": [...], "b": [...]},
}
```

For each metric it runs `paired_ttest()` and `cohens_d()`, collects every metric's p-value into one list, corrects that list with `bonferroni_correct()`, then attaches each metric's *corrected* significance (not the raw, uncorrected one) back onto its result.

Sample output on real data (5 paired test cases per metric):

```text
{
  "metrics": {
    "accuracy": {
      "statistic": -6.32, "p_value": 0.0032,
      "cohens_d": -0.55, "interpretation": "medium",
      "significant_corrected": True
    },
    "latency": {
      "statistic": 5.00, "p_value": 0.0075,
      "cohens_d": 0.79, "interpretation": "medium",
      "significant_corrected": True
    }
  },
  "corrected_alpha": 0.025
}
```

Note: `corrected_alpha = 0.05 / 2 = 0.025` here because two metrics were compared. Both metrics stay significant even under the stricter threshold — but a metric with, say, p_value = 0.03 would have passed at the standard α=0.05 and failed after correction.

## Key implementation notes

- Every function returns a plain `dict`, no LLM calls — pure statistical functions on lists/arrays, consistent with the metric contract established in `14-custom-metrics`.
- Numeric fields returned by scipy/numpy come back as `np.float64`/`np.bool_`, not native Python types. Not an issue for internal use, but relevant if these results are ever serialized to JSON for a report — `json.dumps()` doesn't know how to handle numpy scalar types directly.
- `report.py` assumes dict insertion order matches the order p-values were appended to the list (guaranteed in Python 3.7+), so each metric's corrected significance lines up correctly via `enumerate()`.
- Choosing `paired_ttest` vs `mann_whitney` depends on whether the two groups are the *same* test cases under two conditions (paired) or genuinely independent/non-overlapping data — not on sample size.

## Tests

14 pytest tests, minimum 2 per module, covering both positive/expected-behavior cases and edge cases (`ValueError` on mismatched lengths, correct threshold arithmetic, CI sanity checks).

```powershell
.\venv\Scripts\Activate.ps1
pytest tests/ -v
```

## Environment

Python 3.14, Windows, PyCharm, PowerShell. Flat project structure (`stats/` + `tests/`, no `src/`), `conftest.py` inserting project root into `sys.path`, `pytest.ini` scoping test discovery to `tests/`.

Dependencies: `scipy`, `numpy`, `statsmodels`, `pytest`.