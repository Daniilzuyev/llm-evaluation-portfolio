# 20-langfuse: Langfuse tracing and experiments for a RAG support bot

Instrumentation of the Imagine Bank support bot (retrieve → build context → generate) with Langfuse: traces with token usage and cost, a 12-case dataset, two evaluators and two experiments on identical data. The pipeline, dataset and evaluators are copied from `19-langsmith`, so the two tools can be compared on the same bot, the same cases and the same judge.

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

Pinned versions (same SDK versions as `19-langsmith` where applicable): `anthropic==0.125.0`, `langfuse==4.16.0`, `pytest==9.1.1`, `python-dotenv==1.2.3`, `python-frontmatter==1.3.0`.

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
- Why 3 items flipped is not verified in traces. Items 5 and 8 are consistent with the plural-handling mechanism found in `19-langsmith`; item 7 may be wording variance, because `temperature` is not set in the bot call.
- The baseline run was executed on 2026-10-03, the tokenize-singular run on 2026-10-02. Code, dataset, prompt and models were the same.

### Known issues carried over from `19-langsmith` (reproduced here)

- The retriever returns a third, irrelevant chunk (matched only by the word "card"). The model ignores it.
- The bot does not follow "reply exactly": it appends text after "I don't have that information."
- `no_phone_number` never fires in these runs (12 of 12 in both).
- The `stale_data` case fails in every run.
- The expected answer of the "daily limit for transfers to other banks" case also requires the monthly limit, although the query asks only for the daily one (dataset defect from `19-langsmith`).

## Same data, two tools

Both projects use the same bot, the same 12 cases, the same two evaluators and the same one-line change between experiments.

| | `19-langsmith` baseline | `19-langsmith` tokenize-singular | `20-langfuse` baseline | `20-langfuse` tokenize-singular |
|---|---|---|---|---|
| `matches_expected` | 9 of 12 | 10 of 12 | 8 of 12 | 11 of 12 |
| Input tokens | 1946 | 2053 | 1946 | 2053 |
| Output tokens | 817 | 927 | 833 | 889 |

- Input tokens are identical in both tools, so retrieval and context are reproduced exactly.
- Output tokens and `matches_expected` differ between the tools. Both are consistent with model non-determinism (`temperature` is not set; the default was not checked). The difference between tools is not attributed to either tool.
- Latency is not compared: the `19-langsmith` figures (P50 1.02 s and 1.19 s) come from the LangSmith experiment table, where it is not recorded which span they measure; the figures in this README are the root `answer_pipeline` observation.

## LangSmith vs Langfuse: observations from this portfolio

Everything below comes from the two projects (`19-langsmith`, `20-langfuse`). There are no general claims about either tool. "Not recorded" means the project notes contain no observation, not that the feature is absent.

| Area | LangSmith (`19-langsmith`, `langsmith==0.14.1`) | Langfuse (`20-langfuse`, `langfuse==4.16.0`) |
|---|---|---|
| Setup | `wrap_anthropic` failed on `anthropic` 1.x with `AttributeError: 'Anthropic' object has no attribute 'completions'`. Fix: pin `anthropic<1` (installed 0.125.0). Not tested with newer `langsmith` releases | Plain `anthropic.Anthropic()` client, no wrapper; no setup breakage recorded |
| Tracing API | `@traceable` decorator; `wrap_anthropic(anthropic.Anthropic())` for the model call | `@observe()` decorator; `as_type="generation"` for LLM calls; SDK 4.16.0 is built on OpenTelemetry |
| Token usage | Recorded through the wrapped client; no manual usage call in `app/generator.py` | Set manually with `update_current_generation(usage_details=...)`. Keys `input` / `output` are mapped (192 / 43 in one trace); keys `prompt_tokens` / `completion_tokens` gave input 0, output 0, total 235 |
| Cost | Shown per experiment in the UI: $0.0061 (baseline), $0.0067 (tokenize-singular), bot calls only | Calculated from model and usage; one trace showed $0.000407; per experiment $0.006111 and $0.006498 (via `run_stats.py`) |
| Dataset items | `create_examples(dataset_name=..., examples=[{"inputs", "outputs", "metadata"}])`. The upload script skips an existing dataset, so editing cases means deleting the dataset in the UI and uploading again | `create_dataset_item(..., id=...)` upserts by id, so re-running the upload does not duplicate items (two runs, 12 items) |
| Experiment API | `Client().evaluate(target, data=..., evaluators=[...], experiment_prefix=...)`. Target takes `inputs: dict` and returns a dict. Evaluators declare only the arguments they use (`inputs`, `outputs`, `reference_outputs`) and return a bool or `{"key", "score", "comment"}` | `dataset.run_experiment(name, task, evaluators, max_concurrency)`. Task signature `task(*, item, **kwargs)`; evaluator signature `(*, input, output, expected_output, metadata, **kwargs)` returning `{"name", "value", "comment"}` |
| Experiment naming | `experiment_prefix` plus a generated suffix, for example `baseline-haiku-47ea1ae4` | Name is stored with a UTC timestamp suffix |
| UI: comparing runs | Side-by-side comparison of two experiments | Compare view shows per-metric averages, deltas and improved / regressed counters per item |
| UI: run-level totals | Experiment table shows latency P50, total tokens and cost per experiment | Summary block shows scores only. No run-level P50 latency, tokens or cost; per-item latency and cost are available as columns. Run-level figures required `experiments/run_stats.py` |
| UI: list output | `retrieve` → Output showed the empty list for the case where retrieval failed. No display problem recorded | The Formatted view of the `retrieve` output (a list) hid item 0; the Raw view showed all 3 (cause not verified) |
| Programmatic reads | Not used in `19-langsmith` | Legacy endpoints return HTTP 410 `LEGACY_API_UNAVAILABLE_FOR_NEW_ORGANIZATION` for organizations created on or after 2026-09-16. `get_dataset_run` and `api.trace.get` failed this way; use `api.experiments.list_items` and `api.observations.get_many` (v2) |
| Data freshness | UI averages lagged while evaluator results arrived (baseline 0.67, then 0.75 after reload) | The API response states that non-OpenTelemetry reads can lag by up to 10 minutes |

### Not verified

- Token rates ($1 / $5 per 1M tokens) were inferred from arithmetic, not checked against a pricing page.
- A reported cut of the LangSmith maximum trace retention (400 to 180 days, September 2026) came from a documentation search during `19-langsmith`; check the current LangSmith documentation before relying on it.
- Each experiment ran once per tool, so latency differences between variants and between tools are not conclusions.
- The `wrap_anthropic` failure was observed with `langsmith==0.14.1` only.

### Takeaway

On this dataset the main cost with LangSmith was SDK compatibility (`wrap_anthropic` vs `anthropic` 1.x). The main costs with Langfuse were API drift (HTTP 410 on legacy endpoints) and missing run-level totals in the UI. The data does not support an overall "better tool" verdict.

APIs change quickly. Verify method names against the current documentation and the installed SDK before relying on them (`https://langfuse.com/docs`, `https://docs.smith.langchain.com`).

## Status

- [x] Tracing with tokens and cost
- [x] Dataset of 12 cases with `failure_mode`
- [x] Two experiments on the same data, reported as "N of 12"
- [x] Offline pytest suite, green
- [x] Side-by-side observations for LangSmith and Langfuse