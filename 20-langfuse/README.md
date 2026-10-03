# 20-langfuse — Langfuse tracing and experiments for a RAG support bot

Instrumentation of the Imagine Bank support bot (retrieve → build context → generate) with Langfuse: traces with token usage and cost, a 12-case dataset, two evaluators and two experiments on identical data. The pipeline is copied from `19-langsmith` so that T25 can compare Langfuse and LangSmith under the same conditions.

## What is in this project

| Path | Purpose |
|---|---|
| `app/corpus.py` | Loads bank documents from `data/bank_docs/` into chunks |
| `app/retriever.py` | Keyword retriever (`tokenize`, `singular`, `retrieve`) |
| `app/generator.py` | Builds context, calls Claude, records model, parameters and token usage on the generation |
| `app/pipeline.py` | `answer_pipeline`: retrieve → build_context → generate_answer |
| `data/eval_cases.py` | 12 test cases: `query`, `expected`, `failure_mode` |
| `datasets/upload_dataset.py` | Uploads the cases to a Langfuse dataset (idempotent, fixed item ids) |
| `experiments/evaluators.py` | `no_phone_number` (regex) and `matches_expected` (LLM judge) |
| `experiments/run_experiment.py` | Runs one experiment on the dataset |
| `experiments/run_stats.py` | Run-level P50 latency, tokens and cost through the Langfuse API |
| `experiments/list_names.py` | Lists experiment names stored in Langfuse |
| `tests/` | Offline pytest tests (no network, no real API key) |

## Setup

Python 3.14, Windows, PowerShell.

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` in the project root (it is listed in `.gitignore`, never commit it):

```
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
ANTHROPIC_API_KEY=...
```

Pinned versions (same SDK versions as `19-langsmith`): `anthropic==0.125.0`, `langfuse==4.16.0`, `pytest==9.1.1`, `python-dotenv==1.2.3`, `python-frontmatter==1.3.0`.

## Run

Run modules from the project root as `py -m package.module`.

```powershell
py -m datasets.upload_dataset
py -m experiments.run_experiment baseline
py -m experiments.list_names
py -m experiments.run_stats "<full experiment name from list_names>"
py -m pytest -v
```

Langfuse stores the experiment name with a UTC timestamp suffix, for example `baseline - 2026-10-03T08:25:11.152381Z`. Use the full name with `run_stats`.

## Tests

`py -m pytest -v` → 8 passed (retriever: `singular`, `tokenize`; evaluator: `no_phone_number`; import smoke test). `conftest.py` sets `LANGFUSE_TRACING_ENABLED=false` and a placeholder `ANTHROPIC_API_KEY`, so the tests make no network calls. The LLM judge `matches_expected` is not covered by offline tests because it calls the API.

## Experiments

Dataset `imagine-bank-support-qa`: 12 items, each with `failure_mode` in metadata. The only variable between the two runs is one line in `app/retriever.py`:

| | baseline | tokenize-singular |
|---|---|---|
| Change | `tokens.add(word)` | `tokens.add(singular(word))` |
| `matches_expected` | 8 of 12 | 11 of 12 |
| `no_phone_number` | 12 of 12 | 12 of 12 |
| Items better / worse (Langfuse compare view) | reference | 3 better, 0 worse |
| Input tokens | 1946 | 2053 |
| Output tokens | 833 | 889 |
| Cost (bot calls only) | $0.006111 | $0.006498 |
| P50 latency (`answer_pipeline`, root observation) | 2.265 s | 2.526 s |

Bot model: `claude-haiku-4-5`, `max_tokens=300`. Judge model: `claude-sonnet-5`. Concurrency: 1.

How to read the numbers:

- Counts are reported as "N of 12", not averages. With 12 cases one item is 8.3 percentage points.
- Cost and tokens cover the bot only. Judge calls are not traced, so their tokens and cost are not included.
- Cost matches $1 per 1M input tokens and $5 per 1M output tokens (1946 × $1/M + 833 × $5/M = $0.006111). These rates are inferred from the calculation, not verified against a pricing page.
- Latency: one run per variant, no repeats. The 0.261 s difference is not a conclusion because run-to-run variance is unknown.
- Why 3 items flipped is not verified in traces. Items 5 and 8 are consistent with the plural-handling mechanism found in T23; item 7 may be wording variance, because `temperature` is not set in the bot call.
- The baseline run was executed on 2026-10-03, the tokenize-singular run on 2026-10-02. Code, dataset, prompt and models were the same.

### Known issues carried over from T23 (reproduced here)

- The retriever returns a third, irrelevant chunk (matched only by the word "card"). The model ignores it.
- The bot does not follow "reply exactly": it appends text after "I don't have that information."
- `no_phone_number` never fires in these runs (12 of 12 in both).
- The `stale_data` case fails in every run.
- The expected answer of the "daily limit for transfers to other banks" case also requires the monthly limit, although the query asks only for the daily one (dataset defect from T23).

## Differences from LangSmith (facts observed in Langfuse)

Observations from this project. The LangSmith column is TBD and is filled in T25 from `19-langsmith`.

| Area | Langfuse (observed in this project) | LangSmith |
|---|---|---|
| Tracing API | `@observe()` decorator; `as_type="generation"` for LLM calls; SDK 4.16.0 is built on OpenTelemetry | TBD |
| Token usage | Set manually with `update_current_generation(usage_details=...)`. Keys `input` / `output` are mapped (192 / 43 in one trace); keys `prompt_tokens` / `completion_tokens` gave input 0, output 0, total 235 | TBD |
| Cost | Calculated from model and usage; one trace showed $0.000407 | TBD |
| Dataset items | `create_dataset_item(..., id=...)` upserts by id, so re-running the upload does not duplicate items (two runs, 12 items) | TBD |
| Experiment API | `dataset.run_experiment(name, task, evaluators, max_concurrency)`; task signature `task(*, item, **kwargs)`; evaluator signature `(*, input, output, expected_output, metadata, **kwargs)` returning `{"name", "value", "comment"}` | TBD |
| Experiment naming | Name is stored with a UTC timestamp suffix | TBD |
| UI: comparing runs | Compare view shows per-metric averages, deltas and improved / regressed counters per item | TBD |
| UI: run-level totals | Summary block shows scores only. No run-level P50 latency, tokens or cost; per-item latency and cost are available as columns | TBD |
| UI: list output | The Formatted view of the `retrieve` output (a list) hid item 0; the Raw view showed all 3 (cause not verified) | TBD |
| Programmatic reads | Legacy endpoints return HTTP 410 `LEGACY_API_UNAVAILABLE_FOR_NEW_ORGANIZATION` for organizations created on or after 2026-09-16. `get_dataset_run` and `api.trace.get` failed this way; use `api.experiments.list_items` and `api.observations.get_many` (v2) | TBD |
| Data freshness | The API response states that non-OpenTelemetry reads can lag by up to 10 minutes | TBD |

APIs change quickly. Verify method names against the current Langfuse documentation and the installed SDK before relying on them (`https://langfuse.com/docs`).

## Status

- [x] Tracing with tokens and cost
- [x] Dataset of 12 cases with `failure_mode`
- [x] Two experiments on the same data, reported as "N of 12"
- [x] Offline pytest suite, green
- [x] README with differences from LangSmith (LangSmith column to be completed in T25)