# LLM-as-Judge for Summarization Quality Evaluation

Production-style LLM-as-Judge that evaluates summaries on **3 independent axes**:
faithfulness, completeness, and conciseness. Calibrated against an adversarial
test set covering 4 failure modes (hallucinations, omissions, verbosity, factual errors).

## Use case

Customer support tickets are summarized by LLM-generators for daily management
reports. A bad summary can hide critical urgency, scale, or business impact —
directly affecting escalation decisions. This evaluator detects summarization
failures **before** they reach stakeholders.

## Architecture

- **Judge model:** `claude-sonnet-4-20250514`
- **Generator model:** *out of scope — this project evaluates summaries, doesn't generate them*
- **Temperature:** `0` (deterministic for CI/CD reproducibility)
- **Output:** structured JSON with per-criterion breakdown

```
┌─────────────────┐         ┌──────────┐         ┌─────────────────┐
│  Original text  │────┐    │          │    ┌───→│  score (1-5)    │
└─────────────────┘    ├───→│  Judge   │────┤    │  reasoning      │
┌─────────────────┐    │    │ (Claude) │    └───→│  criteria{3}    │
│     Summary     │────┘    │          │         └─────────────────┘
└─────────────────┘         └──────────┘
```

## Evaluation criteria

| Criterion        | What it catches                                       |
|------------------|-------------------------------------------------------|
| **Faithfulness** | Hallucinated or distorted facts not in original       |
| **Completeness** | Missing key facts, urgency, scale, or business impact |
| **Conciseness**  | Filler phrases, verbose constructions, redundancy     |

## Calibration results (5 adversarial test cases)

| Test case | Failure mode      | Expected | Got   | Diagnostic criterion           |
|-----------|-------------------|----------|-------|--------------------------------|
| TC-01     | None (baseline)   | 4-5      | **5** | All 5/5                        |
| TC-02     | Hallucinated fact | 1-2      | **2** | faithfulness=1                 |
| TC-03     | Incomplete        | 2-3      | **3** | completeness=2                 |
| TC-04     | Verbose           | 2-3      | **3** | conciseness=2                  |
| TC-05     | Wrong facts       | 1-2      | **1** | faithfulness=1, completeness=1 |

**Result:** 5/5 within expected range. The judge correctly attributes each
failure to the right criterion — confirming the rubric isolates each failure mode.

## Bias mitigation

The system prompt includes explicit rules against three known LLM-as-Judge biases:

- **Length bias:** "Summary length is NOT a criterion."
- **Style bias:** "Writing style is NOT a criterion."
- **Self-preference bias:** "Do NOT reward summaries matching your own style."

## Limitations & honest assessment

- TC-04 (verbose) showed a completeness regression (3/5) because the verbose
  summary unintentionally omitted some facts. A purely isolated verbose test
  would require preserving 100% of original facts while only adding verbosity.
- Dataset is small (5 cases) — sufficient for calibration demo, not for
  statistical significance testing.
- Single-judge architecture — no inter-judge agreement (Cohen's kappa) measured.
  A production system would use 2-3 judges and reconcile disagreements.

## Setup

```powershell
cd 12-llm-as-judge
py -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

## Run

```powershell
# All tests (calls real Anthropic API, costs ~$0.05)
py -m pytest

# Only judge tests
py -m pytest -m judge

# Diagnostic calibration report
py inspect_judge.py
```

## Tech stack

- Python 3.14
- `anthropic` SDK (direct, no LangChain)
- `pytest` + `@pytest.mark.parametrize`
- `python-dotenv` for secrets

## What I learned

- **A good rubric matters more than a good model.** Vague criteria like "is this
  summary good?" produced random scores. Switching to three clear axes with
  explicit 1-5 anchors made the judge consistent.

- **Per-criterion scores show *why* a summary failed.** One overall score tells
  you something is broken. Three separate scores tell you exactly what — hallucination,
  missing facts, or too much fluff.

- **Each test case should target one failure mode.** My verbose test accidentally
  also dropped facts, and the judge caught both — useful reminder that
  "one assertion per test" applies to LLM evals too.

- **Anti-bias rules belong in the prompt.** Without explicit "length is not a
  criterion", the judge quietly rewards longer summaries.

- **API keys leak fast.** I leaked mine twice during setup and had to rotate.
  A PowerShell one-liner to update all `.env` files across the portfolio paid
  for itself immediately.
