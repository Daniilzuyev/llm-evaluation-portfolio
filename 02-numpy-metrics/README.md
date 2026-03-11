# Topic 2: NumPy for Metrics Calculation

Class for analyzing LLM evaluation metrics using NumPy vectorized operations.

## Features

- Load evaluation results from CSV
- Calculate 8 basic metrics (mean, median, std, min, max, range, p95, pass_rate)
- Detect anomalies using z-score analysis
- Compare two evaluation runs (A/B testing)
- Save report to JSON

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from metrics_calculator import MetricsCalculator

# Load results
calc = MetricsCalculator('eval_run_baseline.csv')

# Basic statistics
stats = calc.calculate_statistics()
# {'mean': 0.735, 'median': 0.783, 'std': 0.164, ...}

# Detect anomalies
anomalies = calc.detect_anomalies(threshold=2.0)
# [{'index': 4, 'score': 0.21, 'z_score': -3.18}, ...]

# Compare runs
comparison = calc.compare_runs('eval_run_experiment.csv')
# {'baseline_mean': 0.735, 'experiment_mean': 0.805, 'improvement': 0.07}

# Save report
calc.save_report('metrics_report.json')
```

## Key Metrics

- **mean/median** — central tendencies
- **std** — variance in scores
- **p95** — 95th percentile (top 5% results)
- **pass_rate** — percentage of prompts with score ≥ 0.7
- **z-score** — standardized deviation (|z| > 2 → anomaly)
