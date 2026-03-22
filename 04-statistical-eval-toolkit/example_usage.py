import json
from statistical_evaluator import StatisticalEvaluator


with open("example_data/prompt_a_results.json") as f:
    scores_a = json.load(f)

with open("example_data/prompt_b_results.json") as f:
    scores_b = json.load(f)

evaluator = StatisticalEvaluator()

print("=" * 60)
print("STATISTICAL EVALUATION TOOLKIT - DEMO")
print("=" * 60)

# 1. Compare prompts
print("\n1. COMPARE PROMPTS (Paired T-Test)")
print("-" * 60)
result = evaluator.compare_prompts(scores_a, scores_b, test_type="paired")
print(f"Prompt A mean: {result['mean_a']:.3f}")
print(f"Prompt B mean: {result['mean_b']:.3f}")
print(f"P-value: {result['p_value']:.6f}")
print(f"Statistically significant: {result['significant']}")
print(f"Effect size (Cohen's d): {result['effect_size']:.2f}")

# 2. Confidence intervals
print("\n2. CONFIDENCE INTERVALS (95%)")
print("-" * 60)
ci_a = evaluator.confidence_interval(scores_a)
ci_b = evaluator.confidence_interval(scores_b)
print(f"Prompt A: [{ci_a[0]:.3f}, {ci_a[1]:.3f}]")
print(f"Prompt B: [{ci_b[0]:.3f}, {ci_b[1]:.3f}]")

# 3. Required sample size
print("\n3. REQUIRED SAMPLE SIZE")
print("-" * 60)
for effect in [0.2, 0.5, 0.8]:
    n = evaluator.required_sample_size(effect_size=effect)
    effect_name = {0.2: "Small", 0.5: "Medium", 0.8: "Large"}[effect]
    print(f"{effect_name} effect (d={effect}): {n} tests needed")

# 4. Visualization
print("\n4. VISUALIZATION")
print("-" * 60)
print("Opening plot...")
evaluator.plot_comparison(scores_a, scores_b)