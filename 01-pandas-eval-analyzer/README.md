# Eval Dataset Analyzer

Utility for analyzing LLM evaluation run results.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```python
from eval_analyzer import EvalAnalyzer

analyzer = EvalAnalyzer()
analyzer.load_data('sample_eval.csv')

# Filter by score
high_performers = analyzer.filter_by_score(0.8)

# Compare models
comparison = analyzer.model_comparison()
print(comparison)

# Export failed tests
analyzer.export_failed_tests('failed_tests.csv', threshold=0.7)
```

## Data Format

Required columns:
- `prompt_id` — unique test ID
- `model` — model name
- `score` — evaluation score (0.0 - 1.0)

Optional:
- `latency_ms` — response time in milliseconds
- `prompt_text`, `response` — text data

## Methods

- `load_data(filepath)` — load CSV/JSON
- `filter_by_score(min_score)` — filter by score threshold
- `model_comparison()` — statistics by model
- `export_failed_tests(output_path, threshold)` — export failed tests