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

## Key Metrics

- **mean/median** — central tendencies
- **std** — variance in scores
- **p95** — 95th percentile (top 5% results)
- **pass_rate** — percentage of prompts with score ≥ 0.7
- **z-score** — standardized deviation (|z| > 2 → anomaly)
