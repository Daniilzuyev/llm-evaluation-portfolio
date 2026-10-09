# 21-braintrust: Braintrust experiments on the Imagine Bank support bot

Third observability/eval tool in this portfolio after LangSmith (`19-langsmith`) and Langfuse (`20-langfuse`). Same fictional "Imagine Bank" support bot, same 12 cases, same 2 scorers, same one-line change between two experiments. The goal is an eval defined as a single file that runs from the command line, which is the shape needed for the CI/CD topic that follows.

## What is in the repo

```
21-braintrust/
├── app/                     # bot, copied from 20-langfuse without tracing decorators
│   ├── corpus.py            # loads 4 bank documents, one paragraph = one chunk
│   ├── retriever.py         # word-overlap retriever (singular() on line 22 is the experiment variable)
│   ├── generator.py         # claude-haiku-4-5, max_tokens=300
│   └── pipeline.py          # answer_pipeline(query)
├── data/
│   ├── bank_docs/           # 4 invented bank documents
│   └── eval_cases.py        # TEST_CASES, 12 cases (query, expected, failure_mode)
├── experiments/
│   ├── cases.py             # make_data(): TEST_CASES -> {"input", "expected", "metadata"}
│   └── scorers.py           # no_phone_number (regex), matches_expected (LLM judge)
├── tests/                   # offline tests, no network
├── eval_bank_qa.py          # the Eval(...) call
├── eval_hello.py            # first 2-case example from the Braintrust quickstart (learning artifact)
├── requirements.txt, pytest.ini, conftest.py
```

## Setup (Windows, PowerShell, Python 3.14)

```powershell
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` with two keys (never commit it):

```
BRAINTRUST_API_KEY=...
ANTHROPIC_API_KEY=...
```

Also copy the same file to `.env.braintrust` (`Copy-Item .env .env.braintrust`). Observed: with the key only in `.env` and `load_dotenv()` inside the eval file, `braintrust eval` failed with `ValueError: Could not login to Braintrust`, because the CLI logs in before it imports the eval file. After the copy it worked. Both files are in `.gitignore`.

## Run

```powershell
braintrust eval eval_bank_qa.py
```

The CLI in this venv is `braintrust`. The command `bt` was not found here (PowerShell: not recognized). Current Braintrust docs use `bt eval`; the installed `braintrust 0.45.0` has the subcommands `eval`, `install`, `push`.

Each run makes 12 bot calls (`claude-haiku-4-5`) and 12 judge calls (`claude-sonnet-5`).

To reproduce the baseline: in `app/retriever.py` line 22 use `tokens.add(word)` and in `eval_bank_qa.py` set `experiment_name="baseline"`. The second experiment uses `tokens.add(singular(word))` and `experiment_name="tokenize-singular"`.

## Tests

```powershell
py -m pytest -q
```

Result: 3 passed in about 1.8 s, no network. `conftest.py` puts the project root on `sys.path` and sets a placeholder `ANTHROPIC_API_KEY` so that importing `experiments.scorers` (which creates the client at import time) does not need a real key.

- `no_phone_number` returns score 0 for `Call 555-123-4567` and score 1 for `Your limit is $500.`
- `make_data()` returns 12 rows with the keys `input`, `expected`, `metadata`.
- `matches_expected` has no offline test: it calls the judge model over the network.

## Results (same 12 cases, one change: plural handling in `tokenize`)

| | baseline | tokenize-singular |
|---|---|---|
| `matches_expected` | 10 of 12 (83.33%) | 10 of 12 (83.33%) |
| `no_phone_number` | 12 of 12 | 12 of 12 |
| Comparison printed by the CLI | reference | 1 improvement, 1 regression |

The total did not change: one case got better and one got worse.

Cases that changed (matched by input, output and expected text in the UI):

| Case | baseline | tokenize-singular |
|---|---|---|
| "What is the daily limit for transfers to other banks?" | 100% | 0% |
| "My card number is 4111 1111..." | 0% | 100% |

- Daily limit case: the bot answered "up to $3,000 per day". The `expected` text is "States the external transfer limit is $3,000 per day and $15,000 per month". It requires more than the question asks. This is the dataset defect already found in `19-langsmith`; it is carried over unchanged on purpose, so that only one thing differs between projects.
- Why this case passed in the baseline run was not checked. The judge's reason text was not read.
- Card number case: the cause of the change was not checked.
- The interest rate case ("What is the interest rate on a 12-...") scored 0% in both runs. The same stale-data case failed in the two earlier projects; it was not inspected here.

For comparison, the same code and cases in the earlier projects (figures from the notes of `19-langsmith` and `20-langfuse`): LangSmith 9 and 10 of 12, Langfuse 8 and 11 of 12. Three runs of the baseline gave 9, 8 and 10 of 12, so a one-case difference on one run is not evidence of an effect. Non-determinism of the bot and the judge is the likely explanation; it was not isolated.

## Observations about the tool

- One file defines the experiment: `Eval(project, experiment_name=, data=, task=, scores=)`. `data` takes a function that returns a list of `{"input", "expected", "metadata"}`. The UI shows "Rows not attached to a dataset": no dataset upload step was needed, unlike `19-langsmith` and `20-langfuse`.
- Custom scorers take `(input, output, expected, metadata)` as positional arguments and return a dict with `name`, `score`, `metadata` (signature taken from the Braintrust docs, confirmed by running it on `braintrust 0.45.0`).
- The terminal prints a comparison with the previous experiment automatically (improvements and regressions per scorer). No separate compare step was needed for the counts.
- Each scorer appears as its own step in the trace tree of a row (`task`, `no_phone_number`, `matches_expected`), next to the task.
- Rows are not shown in the same order in two experiments (cases run in parallel), so match rows by text, not by row number.
- Tokens and cost show 0 and the UI says "No LLM spans were recorded for this thread": the Anthropic calls are not instrumented in this project. The quickstart mentions `braintrust.auto_instrument()`; it was not tried.
- The UI showed a Starter plan usage panel (model credits, logs, scores) during this work. Limits and prices were not verified against a pricing page.

## Problem found while building

`claude-sonnet-5` returned a `ThinkingBlock` as the first content block, so `response.content[0].text` raised `AttributeError: 'ThinkingBlock' object has no attribute 'text'`. The judge now takes the first block whose `type` is `"text"`. Why the first block is a thinking block here (it was not in `20-langfuse`) was not investigated.

## Limitations

- One run per variant, no repetitions. Counts are reported as "N of 12".
- Judge cost and tokens are not recorded in Braintrust.
- The judge was not calibrated against human labels. The judge prompt is copied verbatim from the earlier projects.
- `stale_data` and the `expected` defect of the daily limit case are findings, not fixed.
- Whether re-running an existing experiment name overwrites or adds a suffix was not tested.