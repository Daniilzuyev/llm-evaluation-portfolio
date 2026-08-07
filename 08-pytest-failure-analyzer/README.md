# 08 — Pytest Failure Analyzer

LLM failure classification system built with Python and Anthropic SDK, **covered by an automated pytest suite**.
Extends the rule-based classifier from `07-failure-analysis-engine` with unit tests for each detector — the focus of this topic (T14).

## What It Does

Sends prompts to Claude, classifies each response into one of 4 failure types (or `None` if valid), and generates a report. A pytest suite asserts each detector fires when it should — and stays silent when it shouldn't:

| Failure Type | Detection Method | Example |
|---|---|---|
| `refusal` | Keyword patterns | Model declines privacy-violating request |
| `format_error` | JSON parse attempt | Model returns text when JSON expected |
| `hallucination` | Negative signal patterns | Model describes non-existent feature |
| `irrelevance` | Clarification patterns | Model goes off-topic |

## Key Design Decisions

**Priority order matters** — refusal is checked first because it's a terminal state; no further analysis needed.

**Hallucination detection is contextual** — only triggered when `failure_type_expected == "hallucination"`. A confident answer on a valid question is correct, not a hallucination.

**Detection by negative signal** — hallucination/irrelevance are inferred from the *absence* of an honesty or clarification phrase; if the model admits "I don't have that information", it is not a hallucination.

**Prompt caching** — `cache_control: ephemeral` on system prompt reduces token costs on repeated runs.

**Separation of concerns** — `failure_analyzer.py` handles API calls and classification logic; `report_generator.py` handles output formatting.

## Test Suite

`tests/test_failure_analyzer.py` covers each detector with a pytest fixture that supplies a fresh `FailureAnalyzer`. `tests/conftest.py` inserts the project root into `sys.path` so tests can import from the parent directory.

| Test | Verifies |
|---|---|
| `test_refusal_detection` | refusal keyword -> `"refusal"` |
| `test_hallucination_detection` | fabricated feature -> `"hallucination"` |
| `test_format_error_detection` | invalid JSON when JSON expected -> `"format_error"` |
| `test_valid_response` | a good answer returns `None` (no false positive) |
| `test_empty_input` | empty prompt/response returns `None` |

**Known coverage gaps (next steps):** `irrelevance` detection is untested; no happy-path test for valid JSON; priority order (refusal beats format_error) is not asserted.

## Limitations

Rule-based classifier understands surface patterns, not meaning. It misclassifies when the model honestly admits uncertainty (false negative) or when a wrong answer contains the expected keywords (false positive). This is expected behavior — and the motivation for LLM-as-Judge (implemented in `12-llm-as-judge`, T18).

## Project Structure

```
08-pytest-failure-analyzer/
├── failure_analyzer.py     # FailureAnalyzer class — core logic
├── report_generator.py     # generate_report() — output formatting
├── main.py                 # demo run over sample test cases
├── pytest.ini              # testpaths = tests, addopts = -v
├── requirements.txt
├── .env                    # API key (gitignored)
└── tests/
    ├── conftest.py         # sys.path insert for imports
    ├── __init__.py
    └── test_failure_analyzer.py
```

## Setup

```bash
pip install -r requirements.txt
```

Create `.env`:
```
ANTHROPIC_API_KEY=your_key_here
```

## Run

Demo run:
```bash
py main.py
```

**Output:**
```
FAILURE ANALYSIS REPORT
=======================
Total cases: 3
Matches: 2
Accuracy: 67%
```

Test suite:
```bash
py -m pytest -v
```

## Tech Stack

- Python 3.12+
- Anthropic SDK (`claude-sonnet-4-20250514` — deprecated, update on next revision)
- Prompt caching (`cache_control: ephemeral`)
- pytest (fixtures + `conftest.py` sys.path setup)

## Part of

[LLM Evaluation Portfolio](https://github.com/Daniilzuyev/llm-evaluation-portfolio) — a structured curriculum for transitioning into LLM Evaluation Engineering.