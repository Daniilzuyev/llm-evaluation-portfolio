# Custom Metrics — Domain-Specific Metric Library

Custom evaluation metrics for LLM outputs, covering structural (rule-based)
and operational (latency/cost) checks. Built as part of an LLM Evaluation
Engineer curriculum (Topic 19).

## Why custom metrics?

Off-the-shelf frameworks (DeepEval, RAGAS) cover generic quality checks
(relevancy, faithfulness). Real production systems always need
business-specific rules that no framework provides out of the box —
e.g. "response must contain a ticket ID", "response must stay under
2s latency", "cost per request must stay under $0.01".

## Architecture

```
metrics/
├── base_metric.py           # MetricResult (dataclass) + BaseCustomMetric (contract)
├── ticket_format_metric.py  # Structural metric: regex-based ticket ID check
├── latency_metric.py        # Operational metric: latency threshold check
└── cost_metric.py           # Operational metric: cost + token count check

tests/
├── test_ticket_format_metric.py
├── test_latency_metric.py
└── test_cost_metric.py

report.py                    # Runs all metrics across test cases, aggregates results
```

## Design decisions

- **BaseCustomMetric contract**: every metric must return a `MetricResult` —
  raises `NotImplementedError` if a subclass forgets to implement `measure()`,
  surfacing the bug immediately instead of a silent `None` downstream.
- **Structural vs operational metrics**: `TicketFormatMetric` is a pure regex
  check on output text (no API-call data needed). `LatencyMetric` and
  `CostMetric` receive already-measured values (`latency_ms`, `cost_usd`,
  `token_count`) as parameters — timing/cost measurement happens at the
  API-call layer, not inside the metric itself.
- **Regex over LLM-as-Judge**: used where the criterion is fully formalizable
  (ticket ID format). LLM-as-Judge is reserved for semantic/subjective checks
  (e.g. tone) — not implemented here, but this is the deciding principle.

## Usage

```python
from metrics.ticket_format_metric import TicketFormatMetric

metric = TicketFormatMetric()
result = metric.measure(input_text="", output_text="Your request is RE-4521.")
print(result)
# MetricResult(name='ticket_format', score=1.0, passed=True, reason='Ticket found: RE-4521', ...)
```

Run the full report (aggregates 3 metrics across sample test cases):
```bash
py report.py
```

Run tests:
```bash
py -m pytest -v
```

## Sample report output

Running `py report.py` against the 3 sample test cases in this repo
produces an aggregated summary like this:

```json
{
  "ticket_format": {
    "scores": [1, 0, 1],
    "passed": 2,
    "failed": 1,
    "avg_score": 0.6667
  },
  "latency_check": {
    "scores": [1.0, 0.0, 1.0],
    "passed": 2,
    "failed": 1,
    "avg_score": 0.6667
  },
  "cost_check": {
    "scores": [1.0, 0.0, 1.0],
    "passed": 2,
    "failed": 1,
    "avg_score": 0.6667
  }
}
```

Each key is a metric name (`MetricResult.name`). Each value shows the raw
scores across all test cases, how many passed/failed against that metric's
threshold, and the average score — the same shape a CI/CD eval gate would
check against a minimum bar (e.g. "fail the build if `avg_score < 0.8`").

## Requirements

- Python 3.14+
- No external dependencies (stdlib only: `re`, `dataclasses`, `typing`)

## Status

Part of a structured 37-topic LLM Evaluation Engineer curriculum,
building toward capstone eval pipelines (T28–T30).