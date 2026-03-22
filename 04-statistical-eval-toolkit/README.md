# Statistical Evaluation Toolkit

A Python toolkit for statistical analysis of LLM evaluation results. Compare prompts, calculate confidence intervals, determine required sample sizes, and visualize results.

## Features

- **Compare Prompts**: Statistical comparison of two prompt variants (paired/independent t-tests)
- **Confidence Intervals**: Calculate 95% CI for evaluation metrics
- **Sample Size Calculator**: Determine how many tests needed to detect an effect
- **Visualization**: Box plots with confidence intervals

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
import json
from statistical_evaluator import StatisticalEvaluator

# Load evaluation results
with open("example_data/prompt_a_results.json") as f:
    scores_a = json.load(f)

with open("example_data/prompt_b_results.json") as f:
    scores_b = json.load(f)

evaluator = StatisticalEvaluator()

# 1. Compare two prompts
result = evaluator.compare_prompts(scores_a, scores_b, test_type="paired")
print(f"P-value: {result['p_value']:.4f}")
print(f"Significant: {result['significant']}")
print(f"Effect size: {result['effect_size']:.2f}")

# 2. Calculate confidence interval
lower, upper = evaluator.confidence_interval(scores_a)
print(f"95% CI: [{lower:.3f}, {upper:.3f}]")

# 3. Determine required sample size
n = evaluator.required_sample_size(effect_size=0.5)
print(f"Tests needed for medium effect: {n}")

# 4. Visualize comparison
evaluator.plot_comparison(scores_a, scores_b)
```

## Interpreting Results

### P-value
- **p < 0.05**: Statistically significant difference (reject null hypothesis)
- **p ≥ 0.05**: No significant difference (fail to reject null hypothesis)

### Effect Size (Cohen's d)
- **0.2**: Small effect
- **0.5**: Medium effect
- **0.8**: Large effect

### Confidence Intervals
- If 95% CIs don't overlap → strong evidence of difference
- If CIs overlap partially → difference may not be significant
- If CIs overlap completely → no meaningful difference

### Paired vs Independent Tests
- **Paired**: Use when comparing same test cases with different prompts (more statistical power)
- **Independent**: Use when test cases are different between prompts

## Example Output
```
1. COMPARE PROMPTS (Paired T-Test)
------------------------------------------------------------
Prompt A mean: 0.794
Prompt B mean: 0.849
P-value: 0.000000
Statistically significant: True
Effect size (Cohen's d): -0.94

2. CONFIDENCE INTERVALS (95%)
------------------------------------------------------------
Prompt A: [0.777, 0.812]
Prompt B: [0.833, 0.864]

3. REQUIRED SAMPLE SIZE
------------------------------------------------------------
Small effect (d=0.2): 394 tests needed
Medium effect (d=0.5): 64 tests needed
Large effect (d=0.8): 26 tests needed
```

## Testing

Run tests with pytest:
```bash
pytest tests/test_evaluator.py -v
```

## Why Statistical Analysis in LLM Evaluation?

Without statistics, you might conclude "Prompt B is better" based on a small sample. Statistical analysis tells you:

1. **Is the difference real?** (p-value)
2. **How big is the difference?** (effect size)
3. **How confident are we?** (confidence intervals)
4. **How many tests do we need?** (sample size calculation)

This prevents false conclusions and helps make data-driven decisions about prompt engineering.

## Dependencies

- numpy >= 1.24.0
- scipy >= 1.10.0
- matplotlib >= 3.7.0
- statsmodels >= 0.14.0
- pytest >= 7.3.0 (for testing)