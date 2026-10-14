# 22-cicd-eval — Eval gate in CI for the Imagine Bank support bot

A CI pipeline that runs an LLM evaluation on every pull request and fails the
pull request when answer quality drops below a threshold. The bot, the 12 test
cases and the 2 scorers are the same as in `21-braintrust`; this project adds
the part that turns scores into a merge decision.

## The problem

Running `braintrust eval` in CI is not enough. In `braintrust==0.45.0` the CLI
returns a non-zero exit code only when an evaluation raises an exception.
Scores do not affect the exit code: a run where the judge passes 0 of 12 cases
still exits with `0`, and CI shows green. (Verified by reading
`braintrust/cli/eval.py` and `braintrust/framework.py` in the installed
package.)

A second problem is judge variance. The LLM judge does not give the same score
on unchanged code, so a threshold set at the best observed run would make CI
fail on random runs (a flaky test).

## How it works

```
pull request
   │
   ├── job offline-tests (every push and PR, no API key, ~20 s)
   │      pytest: scorers, dataset shape, gate logic
   │
   └── job eval-gate (PR only, after offline-tests is green, ~30 s)
          braintrust eval eval_bank_qa.py --no-send-logs --jsonl > summary.jsonl
          python gate/check_scores.py summary.jsonl
              summary.jsonl → passed cases per scorer → compare with thresholds
              any scorer below its threshold → exit 1 → job red
```

- `--no-send-logs` runs the evaluation locally without sending results to
  Braintrust. In this mode the CLI does not log in, so CI needs only
  `ANTHROPIC_API_KEY`, not `BRAINTRUST_API_KEY` (verified in the package
  source; confirmed by the CI runs below).
- `--jsonl` prints the run summary as one JSON line on stdout. HTTP logs go to
  stderr, so `> summary.jsonl` captures only the JSON line (observed locally
  and in CI).
- `eval-gate` runs only on pull requests (`if: github.event_name ==
  'pull_request'`), because every run makes 24 paid API calls. On a plain push
  it is shown as skipped.
- `needs: offline-tests` means no API money is spent when the free tests are
  already red.

## Gate

`gate/check_scores.py` reads the summary, converts each scorer's average score
into a count of passed cases (`round(score * 12)`) and compares it with
`THRESHOLDS`:

| Scorer | Threshold | Why |
|---|---|---|
| `no_phone_number` | 12 of 12 | Regex check, the same answer always gets the same result. Safety check: an invented bank phone number is a real harm, so no failures are allowed. |
| `matches_expected` | 8 of 12 | LLM judge, varies between runs on unchanged code. The threshold sits below the lowest observed run. |

Runs of `matches_expected` on unchanged code (retriever variant
`tokens.add(singular(word))`, same 12 cases, same judge prompt):

| Run | Where | Passed of 12 |
|---|---|---|
| T23 experiment | LangSmith | 10 |
| T24 experiment | Langfuse | 11 |
| T26 experiment | Braintrust | 10 |
| T27 local 1 | `braintrust eval --no-send-logs` | 11 |
| T27 local 2 | `braintrust eval --no-send-logs --jsonl` | 10 |
| T27 CI run #4 | GitHub Actions | 11 |
| T27 CI run #8 | GitHub Actions | 11 |

Observed range: 10–11 of 12 over 7 runs. The threshold of 8 leaves a margin of
2 cases below the lowest observed run. The same judge gave a range of 3 cases
(8–10) on the earlier baseline retriever variant, so a margin of 1 case was
judged too thin.

## Proof that the gate can fail

A check that has never failed may not be able to fail. Pull request #1 contains
a deliberate regression and its revert:

| Commit | Change | `offline-tests` | `matches_expected` | `eval-gate` |
|---|---|---|---|---|
| `6bf6a35` | gate added (run #4) | ✅ | 11 of 12 | ✅ |
| `00f7380` | `retrieve(query, CHUNKS, k=0)` in `app/pipeline.py` (run #6) | ✅ | **5 of 12** | ❌ exit code 1 |
| `40789a0` | revert of `00f7380` (run #8) | ✅ | 11 of 12 | ✅ |

With `k=0` the retriever returns no documents, the bot gets an empty context
and answers "I don't have that information." to almost every question. No
Python error is raised, and the offline tests stay green: they test the
scorers and the gate, not answer quality. Only the evaluation catches this
regression.

`no_phone_number` stayed at 12 of 12 during the regression, as expected: an
empty context does not make the bot invent phone numbers.

Gate log of run #6:

```
no_phone_number 12
matches_expected 5
failed: ['matches_expected']
Error: Process completed with exit code 1.
```

## Project structure

```
22-cicd-eval/
├── app/                    bot: corpus loader, retriever, generator, pipeline (from 21-braintrust)
├── data/                   4 bank documents + 12 test cases (from 21-braintrust)
├── experiments/
│   ├── cases.py            TEST_CASES → Braintrust rows
│   └── scorers.py          no_phone_number (regex), matches_expected (LLM judge)
├── eval_bank_qa.py         Eval(...) definition run by the CLI
├── gate/
│   ├── check_scores.py     summary.jsonl → exit code 0 / 1
│   └── sample_summary.json hand-written summary for manual checks
├── tests/
│   ├── test_cases.py       dataset shape
│   ├── test_scorers.py     no_phone_number on two inputs
│   └── test_gate.py        gate: normal run, judge drop, exactly 8, one phone number
├── azure-pipelines.yml     the same two jobs for Azure Pipelines (not run, see below)
├── conftest.py             project root on sys.path, placeholder API key for offline tests
├── pytest.ini
└── requirements.txt
```

The GitHub Actions workflow is at the repository root:
`.github/workflows/eval-22-cicd.yml`. GitHub reads workflows only from
`.github/workflows/` at the root, and the portfolio is one repository with a
folder per topic. `paths` filters limit the workflow to changes in
`22-cicd-eval/` and the workflow file itself.

## Run locally (Windows, PowerShell)

```powershell
cd 22-cicd-eval
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt

# offline tests, no network
py -m pytest -q

# evaluation + gate (needs ANTHROPIC_API_KEY in .env, 24 API calls)
braintrust eval eval_bank_qa.py --no-send-logs --jsonl --no-progress-bars | Out-File -Encoding utf8 summary.jsonl
py gate\check_scores.py summary.jsonl; echo $LASTEXITCODE
```

`check_scores.py` opens the file with `encoding="utf-8-sig"`. Windows
PowerShell 5.1 writes a byte order mark at the start of UTF-8 files; `utf-8-sig`
skips it when present and changes nothing when it is absent (as in CI on
Linux).

## CI setup

1. Repository → Settings → Secrets and variables → Actions → New repository
   secret `ANTHROPIC_API_KEY`.
2. The key is passed only to the evaluation step (`env:` on that step) and is
   shown as `***` in the logs.
3. GitHub does not pass secrets to workflows triggered by pull requests from
   forks, so `eval-gate` would fail on a fork pull request.

## Cost and time

| | Value | Source |
|---|---|---|
| API calls per evaluation run | 24 (12 bot + 12 judge) | 24 `HTTP/1.1 200 OK` lines in the CI log |
| Bot cost per run | about $0.0065 | T24 Langfuse traces, same bot, same cases, same retriever variant |
| Judge cost per run | not measured | judge calls are not traced |
| `offline-tests` duration | 18–24 s | CI runs #1–#8 |
| `eval-gate` duration | 27–28 s | CI runs #4, #6, #8 |

## Azure Pipelines

`azure-pipelines.yml` contains the same two jobs in Azure Pipelines syntax:

| GitHub Actions | Azure Pipelines |
|---|---|
| `on: push` / `on: pull_request` | `trigger:` / `pr:` |
| `runs-on: ubuntu-latest` | `pool: vmImage: ubuntu-latest` |
| `actions/checkout` | implicit checkout |
| `actions/setup-python` | `task: UsePythonVersion@0` |
| `needs:` | `dependsOn:` |
| `if: github.event_name == 'pull_request'` | `condition: and(succeeded(), eq(variables['Build.Reason'], 'PullRequest'))` |
| `${{ secrets.X }}` | `$(X)`, mapped explicitly with `env:` |

**Not run.** No personal Azure DevOps organization was available, and new
organizations do not get free Microsoft-hosted parallel jobs automatically; the
grant has to be requested and Microsoft states a response time of 2–3 business
days. The file was written from memory of the syntax and was not validated
against the docs or by a run. In particular, the availability of Python 3.14
in `UsePythonVersion@0` on `ubuntu-latest` and the exact `paths` filter format
are unverified.

## Limitations

- **The gate catches large drops only.** With a threshold of 8 and an observed
  range of 10–11, a regression from 11 to 8 passes the gate. Catching smaller
  regressions without flaky failures would need several evaluation runs per
  pull request, which multiplies cost and time.
- **The range is based on 7 runs**, three of them in other tools with tracing
  enabled. The real lower edge of judge variance may be below 10.
- **12 test cases.** Each case is about 8% of the score. `check_scores.py`
  passes `n_cases=12` and the thresholds are counts out of 12; both must change
  when the dataset grows.
- **The judge is not aligned with human labels.** A PASS from the judge has not
  been compared with a human verdict on the same answers.
- **Known dataset defect carried over:** the `expected` text of the "daily
  limit for transfers to other banks" case also requires the monthly limit,
  which the question does not ask for.
- **Which 5 cases passed under `k=0` was not checked.** They are probably cases
  where "I don't have that information" is the correct answer
  (`not_in_kb`, `out_of_scope`); this is a hypothesis.
- **A red gate does not block merging by itself.** Branch protection with
  required status checks is not configured; the red check is a signal, not a
  lock.
- **Runner image change:** GitHub annotated the runs with a notice that the
  `ubuntu-latest` label migrates to Ubuntu 26 from October 19, 2026. The
  workflow does not pin an image version.
- **Python 3.14** was used locally and in CI (`3.14.8` on the runner);
  `braintrust==0.45.0` and the other pinned packages installed and ran on it.

## Time spent

About 6–7 hours (estimate).