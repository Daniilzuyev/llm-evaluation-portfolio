# 07 — Failure Analysis Engine

LLM failure classification system built with Python and Anthropic SDK.  
Detects 4 failure types in LLM responses using a rule-based classifier with ordered priority checks.

## What It Does

Sends prompts to Claude Sonnet, analyzes responses, and classifies failures:

| Failure Type | Detection Method | Example |
|---|---|---|
| `refusal` | Keyword patterns | Model declines privacy-violating request |
| `format_error` | JSON parse attempt | Model returns text when JSON expected |
| `hallucination` | Negative signal patterns | Model describes non-existent feature |
| `irrelevance` | Clarification patterns | Model goes off-topic |

## Key Design Decisions

**Priority order matters** — refusal is checked first because it's a terminal state; no further analysis needed.

**Hallucination detection is contextual** — only triggered when `failure_type_expected == "hallucination"`. A confident answer on a valid question is correct, not a hallucination.

**Prompt caching** — `cache_control: ephemeral` on system prompt reduces token costs on repeated runs.

**Separation of concerns** — `failure_analyser.py` handles API calls and classification logic; `report_generator.py` handles output formatting.

## Limitations

Rule-based classifier achieves **~67% accuracy**. Hallucination detection fails when the model correctly admits uncertainty instead of fabricating an answer. This is expected behavior — and the motivation for LLM-as-Judge (implemented in Topic 19).

## Project Structure

```
07-failure-analysis-engine/
├── failure_analyser.py     # FailureAnalyzer class — core logic
├── report_generator.py     # generate_report() — output formatting
├── requirements.txt
└── .env                    # API key (gitignored)
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

```bash
python failure_analyser.py
```

**Output:**
```
FAILURE ANALYSIS REPORT
=======================
Total cases: 3
Matches: 2
Accuracy: 67%
```

## Tech Stack

- Python 3.12+
- Anthropic SDK (`claude-sonnet-4-20250514`)
- Prompt caching (`cache_control: ephemeral`)

## Part of

[LLM Evaluation Portfolio](https://github.com/Daniilzuyev/llm-evaluation-portfolio) — a structured curriculum for transitioning into LLM Evaluation Engineering.