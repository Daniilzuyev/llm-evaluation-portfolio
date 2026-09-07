# 16-ragas — RAGAS Fundamentals (T21)

Evaluating a RAG (Retrieval-Augmented Generation) pipeline by decomposing it into
retrieval quality vs. generation quality, using [RAGAS](https://github.com/explodinggradients/ragas) `0.4.3`.

## Problem Solved

A single "is this response good?" LLM-as-Judge score (T18/MC-1 pattern) can't tell you
**where** a RAG system failed — bad retrieval and bad generation look identical from the
outside (both produce a bad final answer). RAGAS splits the pipeline into two stages,
each measured two ways:

| Stage | Failure mode caught | Metric |
|---|---|---|
| Retrieval | Retrieved documents are noisy / off-topic | **Context Precision** |
| Retrieval | Needed information wasn't retrieved at all | **Context Recall** |
| Generation | Response contains claims not supported by context | **Faithfulness** |
| Generation | Response doesn't address the actual question | **Answer Relevancy** |

This is the minimal, non-overlapping set: 2 pipeline stages × 2 failure types each = 4 metrics.

## Architecture

```
16-ragas/
├── data/
│   └── sample_qa_dataset.py      # 5 hand-designed mock Q&A cases, one per failure pattern
├── evaluation/
│   ├── config.py                 # judge_llm + embeddings setup (Anthropic + OpenAI)
│   └── run_ragas_eval.py         # Dataset, metrics, @experiment pipeline, entry point
├── tests/
│   └── test_report.py            # unit tests for report.py logic (no live API calls)
├── venv/
│   └── Lib/site-packages/langchain_community/chat_models/vertexai.py  # compat patch, see below
├── conftest.py
├── pytest.ini
└── README.md
```

`evaluation/report.py` holds `THRESHOLDS`, `evaluate_thresholds()`, and `summarize()`.

## The Dataset

5 mock cases (`data/sample_qa_dataset.py`), each engineered to isolate exactly one
failure pattern (or all four at once):

| `case_id` | Faithfulness | Answer Relevancy | Ctx Precision | Ctx Recall | Design intent |
|---|---|---|---|---|---|
| `baseline` | should be high | high | high | high | Everything works |
| `hallucination` | **low** | high | high | high | Response invents an unsupported fact |
| `bad_retrieval` | high | **low** | **low** | **low** | Retriever pulls unrelated docs; response honestly says "I don't know" |
| `off_topic_generation` | high | **low** | high | high | Retrieval is fine, but response answers the topic in general, not the specific question asked |
| `fully_broken` | **low** | **low** | **low** | **low** | Retrieval off-topic AND generation fabricates an answer anyway |

## How Each Score Is Actually Computed

Verified directly from the `ragas==0.4.3` source (`ragas/metrics/collections/`), not just
the docs — the two didn't always agree (see Known Issues).

- **Faithfulness**: LLM decomposes `response` into atomic statements, then NLI-checks
  each against `retrieved_contexts`. `score = supported_statements / total_statements`.
  This is why scores are clean fractions (`0.0`, `0.5`, `1.0`) — not continuous.
- **Answer Relevancy**: LLM generates hypothetical questions from `response`, embeds them,
  and takes mean cosine similarity against the embedded `user_input`. Score is forced to
  `0.0` if the response is judged "noncommittal" (e.g. "I don't know").
  This is why values look continuous/irregular (`0.5701...`) instead of clean fractions.
- **Context Precision / Context Recall**: both use
  `score = numerator / (sum(verdicts) + 1e-10)` — the `1e-10` epsilon prevents
  division-by-zero when nothing is relevant. This is why a "perfect" score prints as
  `0.9999999999`, never a clean `1.0`.

## Thresholds

```python
THRESHOLDS = {
    "faithfulness": 0.5,
    "answer_relevancy": 0.59,
    "context_precision": 0.99,
    "context_recall": 0.99,
}
```

Not arbitrary "nice numbers" — calibrated against real output from this dataset:

- **Faithfulness = 0.5, not 0.8 or 1.0**: `baseline` and `off_topic_generation` were
  *designed* to be fully faithful, but the judge splits their response into 2 statements
  and only confirms 1 as directly supported (see finding below). A threshold of 0.8 would
  fail two correctly-faithful cases — a false positive caused by how the judge decomposes
  text, not by an actual factual error.
- **Answer Relevancy = 0.59**: sits between `off_topic_generation` (0.543, must fail —
  it answers the general topic, not the specific question) and `hallucination` (0.592,
  should pass — the response *is* on-topic, it's just factually wrong, which Faithfulness
  catches separately). The margin here is narrow (~0.05) — a known fragility of this
  threshold on a 5-case dataset; revisit if the dataset grows.
- **Context Precision / Recall = 0.99, not 1.0**: accounts for the `1e-10` epsilon
  artifact above. A literal `>= 1.0` threshold would fail every genuinely perfect case.

## Real Findings From Actual Runs (Not Just Theory)

- **Faithfulness ≠ "is the answer factually correct" in a naive sense.** Both `baseline`
  and `off_topic_generation` were designed so every claim in the response is directly
  traceable to the retrieved context — yet both scored `0.5`, not `1.0`. The judge
  decomposed the response into 2 statements and treated one of them (a restatement of
  the question, e.g. "the timesheet wasn't created") as an unverified claim rather than
  context. **Faithfulness is sensitive to how the LLM chooses to decompose a response
  into atomic statements, not only to literal factual accuracy.**
- **LLM-as-Judge scoring is not fully deterministic in this pipeline.** `baseline`'s
  `context_precision` was `0.99999999995` (effectively 1.0) on one run and `0.50` on a
  later run — same input, same code, different result. Root cause: `temperature`/`top_p`
  had to be stripped from the judge LLM's config entirely (see Known Issues below), so
  there's no way to pin the judge to low-variance output. **Run evals more than once
  before trusting a borderline pass/fail result on this setup.**

## Known Issues / Environment Notes

Ragas `0.4.3` was released against an older `langchain-community` / `anthropic` SDK
surface. Three real incompatibilities surfaced during setup — none are bugs in this
repo's code:

1. **`ModuleNotFoundError: langchain_community.chat_models.vertexai`** — this submodule
   was removed from `langchain-community` after ragas `0.4.3` shipped, but
   `ragas/llms/base.py` still imports it unconditionally at module load, even though we
   never use Google Vertex. Fixed with a one-line compatibility shim placed at
   `venv/Lib/site-packages/langchain_community/chat_models/vertexai.py`:
   ```python
   from langchain_google_vertexai import ChatVertexAI  # noqa: F401
   ```
   **This patch lives inside `venv/` and will need to be reapplied if the venv is ever
   recreated.**

2. **`AsyncMessages.create() got an unexpected keyword argument 'temperature'`** — the
   Anthropic Python SDK removed `temperature`/`top_p`/`top_k` as top-level `messages.create()`
   parameters (replaced by `output_config={"effort": ...}`). Ragas's `InstructorModelArgs`
   still defaults to sending `temperature=0.01, top_p=0.1`. Fixed by stripping both keys
   from the constructed LLM object in `config.py`:
   ```python
   judge_llm.model_args.pop("temperature", None)
   judge_llm.model_args.pop("top_p", None)
   ```
   Side effect: no way to force low-variance judge output — see the non-determinism
   finding above.

3. **`evaluate()` / `aevaluate()` are deprecated** in favor of the `@experiment()`
   decorator + `Dataset`/`InMemoryBackend` pattern used in this repo. Confirmed against
   the official `docs.ragas.io` v0.3→v0.4 migration guide, not just the deprecation
   warning text. `single_turn_score()` (a lower-level, non-deprecated per-metric call)
   was a viable lighter-weight alternative that was considered but not used here, in
   favor of following the officially recommended path.

4. **`MetricResult.reason` is always `None`** in this version. All four collections
   metrics (`Faithfulness`, `AnswerRelevancy`, `ContextPrecision`, `ContextRecall`)
   construct their result as `MetricResult(value=...)` without ever passing `reason=`.
   The `ExperimentResult` schema in this repo still includes `*_reason: Optional[str]`
   fields for forward compatibility, but expect `None` on every run with `0.4.3`.

## Usage

```powershell
cd 16-ragas
venv\Scripts\activate
py -m evaluation.run_ragas_eval
```

Runs all 5 cases through all 4 metrics, prints a per-case pass/fail report against
`THRESHOLDS`, then a summary of `passed/total` per metric.

```powershell
py -m pytest tests/ -v
```

Runs the unit tests (`evaluate_thresholds`/`summarize` logic only — no live API calls,
no cost, no non-determinism; runs in ~0.03s).