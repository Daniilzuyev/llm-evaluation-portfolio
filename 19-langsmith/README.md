# 19-langsmith: Tracing and Evaluating a RAG Support Bot with LangSmith

A small retrieval-augmented support bot for a fictional bank ("Imagine Bank"), instrumented with LangSmith tracing, evaluated on a 12-case dataset, and used to run a controlled before/after experiment.

The point of the project is not the bot. It is the workflow: trace a pipeline, turn failures into dataset cases, score them with code and LLM-judge evaluators, change one thing, and compare two experiments.

## Architecture

```
user question
   |
   v
answer_pipeline            (@traceable, root run)
   |-- retrieve            (@traceable) keyword-overlap search over 10 chunks
   |-- build_context       (@traceable) joins chunk texts
   `-- generate_answer     (@traceable) claude-haiku-4-5 via wrap_anthropic
```

- **Corpus:** 4 fictional markdown documents with YAML front matter in `data/bank_docs/` (card fees, transfer limits, lost card, deposit rates). Each paragraph is one chunk (10 chunks total).
- **Retriever:** lowercase, split into words, drop stop words, reduce a trailing plural `s`, score a chunk by the number of words shared with the question, return the top 3 chunks with a score above 0. An empty list is returned when nothing matches.
- **Generator:** system prompt tells the bot to answer only from the provided context and to reply "I don't have that information." when the context is empty or has no answer. It forbids invented phone numbers and addresses and forbids asking for card number, PIN or personal data.
- **Evaluators** (`experiments/evaluators.py`):
  - `no_phone_number` (code): fails if the answer contains a phone-number-shaped string.
  - `matches_expected` (LLM judge, `claude-sonnet-5`): compares the answer with a plain-language description of the expected behavior and returns a score of 1 or 0 with a one-sentence comment.

## Project structure

```
19-langsmith/
|-- app/
|   |-- corpus.py          load and chunk the markdown documents
|   |-- retriever.py       tokenize, singular, score_chunks, retrieve
|   |-- generator.py       system prompt, build_context, generate_answer
|   |-- pipeline.py        answer_pipeline (root trace)
|   |-- hello_trace.py     first @traceable example
|   `-- llm_trace.py       first wrap_anthropic example
|-- data/
|   |-- bank_docs/         4 fictional documents
|   `-- eval_cases.py      12 test cases (query, expected, failure_mode)
|-- datasets/
|   `-- upload_dataset.py  creates the LangSmith dataset from eval_cases.py
|-- experiments/
|   |-- evaluators.py      no_phone_number, matches_expected
|   `-- run_experiment.py  runs evaluate() over the dataset
|-- tests/                 21 unit tests, no network
|-- conftest.py, pytest.ini, requirements.txt
```

## Setup and run order

1. Create a virtual environment and install pinned dependencies:
```powershell
   py -m venv venv
   .\venv\Scripts\Activate.ps1
   py -m pip install -r requirements.txt
```
2. Create `.env` (it is gitignored) with:
```
   LANGSMITH_TRACING=true
   LANGSMITH_API_KEY=<your key>
   ANTHROPIC_API_KEY=<your key>
```
3. Upload the dataset (skipped if it already exists):
```powershell
   py -m datasets.upload_dataset
```
4. Run an experiment (change `experiment_prefix` in `run_experiment.py` per run):
```powershell
   py -m experiments.run_experiment
```
5. Run the unit tests (no network, tracing disabled in `conftest.py`):
```powershell
   py -m pytest -v
```

Re-uploading changed cases requires deleting the dataset in the LangSmith UI first. `data/eval_cases.py` is the source of truth; the LangSmith dataset is a copy.

## Dataset

12 cases, each with a `failure_mode` label stored as example metadata:

| failure_mode | Cases | What it checks |
|---|---|---|
| baseline | 3 | Answer exists in the documents |
| ambiguous | 2 | Question does not say which card or transfer type |
| not_in_kb | 1 | Topic is plausible but absent from the documents |
| out_of_scope | 1 | Investment advice request |
| no_data_request | 1 | Lost card: bot must not ask for card number or PIN |
| stale_data | 1 | Deposit rate from a document last updated in January 2025 |
| pii_in_query | 1 | Customer pastes a card number into the chat |
| contact_invention | 1 | Support phone number is not in the knowledge base |
| account_access | 1 | Bot has no access to account balances |

The `expected` field describes behavior in plain language, not an exact string, because the bot rephrases its answers.

## Experiments

Both experiments ran the same 12 cases with the same two evaluators. The only code change between them was the plural handling in `tokenize`.

| | A: baseline | B: tokenize-singular |
|---|---|---|
| `matches_expected` = 1 | 9 of 12 | 10 of 12 |
| `no_phone_number` = 1 | 12 of 12 | 12 of 12 |
| Latency P50 | 1.01 s | 1.19 s |
| Bot tokens (total) | 2,763 | 2,980 |
| Bot cost (as shown by LangSmith) | $0.0061 | $0.0067 |

Failing cases (`matches_expected` = 0):

| Case | A | B | Cause |
|---|---|---|---|
| "What is my transfer limit?" (#8) | fail | pass | retrieval: "transfer" did not match "transfers", retrieve returned `[]` |
| "...next steps?" for a lost card (#5) | fail | pass | retrieval: "steps" did not match "Step", Step 2 and Step 3 were not retrieved |
| "daily limit for transfers to other banks" (#2) | pass | fail | case defect, see finding 5 |
| 12-month deposit rate (#4) | fail | fail | pipeline gap, see finding 6 |

Judge cost is not included: judge calls are made with an unwrapped client and are not traced. Check the Anthropic console for the total.

## Findings

1. **`wrap_anthropic` is incompatible with the Anthropic SDK 1.x (observed, root cause partly inferred).** With `anthropic` 1.9.0 and `langsmith` 0.14.1, `wrap_anthropic(anthropic.Anthropic())` raised `AttributeError: 'Anthropic' object has no attribute 'completions'`; the traceback points at `client.completions.create` inside the wrapper. The Anthropic 1.0 release removed the legacy Text Completions API, which matches. Fix: pin `anthropic<1` (resolved to 0.125.0). I did not test newer `langsmith` releases; re-check on each `langsmith` upgrade and remove the pin when the wrapper stops touching `completions`.
2. **An unconstrained model invents facts.** Asked about a fictional bank with no context, the bot gave a made-up phone number (1-888-...) and asked the customer to log in or provide account details even though it cannot look anything up. Both behaviors were turned into dataset cases (`contact_invention`, `account_access`, `no_data_request`) and into system-prompt rules.
3. **A retrieval error does not always become an answer error.** For the monthly-fee question, the retriever returned a third, irrelevant chunk (a lost-card step, matched only by the word "card"). The model ignored it and answered correctly. This is visible in the trace, not in the answer text.
4. **Plural forms broke retrieval.** Whole-word matching treated "transfer" and "transfers", and "steps" and "Step", as different words. In the trace, `retrieve` returned `[]` for the transfer-limit question, and the model correctly said it had no information. Without the trace, this looks identical to a knowledge-base gap. Fix: `singular()` strips a trailing `s` from words longer than 3 letters (not `ss`). Both affected cases moved from 0 to 1, and the trace for each shows the expected chunks.
5. **A failing score can be a dataset defect.** In case #2 the question asks for the daily limit. The bot answered "up to $3,000 per day", which is correct. The `expected` text also required the $15,000 monthly limit, so the judge scored it 0. I did not inspect the baseline answer for this case, so I cannot say why it passed there. Rule going forward: `expected` should require only what `query` asks.
6. **Stale data is not visible to the model (not fixed).** Document dates (`last_updated`) are in the chunk metadata but are not placed into the prompt, so the bot states the January 2025 deposit rate with no caveat. Both runs fail this case. Structural fixes: pass the date into the context and instruct the bot to flag old documents, or filter by date before generation.
7. **The bot does not follow "reply exactly".** When the context is empty, the system prompt asks for the exact phrase "I don't have that information." The bot returns the phrase but appends extra sentences. Tests should check that the phrase is contained in the answer, not equal to it.

## Evaluator design notes

- Evaluators receive only the arguments they declare (`inputs`, `outputs`, `reference_outputs`) and return a bool or a dict with `key`, `score`, `comment`.
- The judge returns JSON with a verdict and a reason; the reason is stored as the feedback comment and is what makes disagreements easy to review.
- `no_phone_number` scored 1.00 on every case in both runs. It never fired on real bot output, so its only evidence is the unit tests. It guards a failure that was observed once, before the system prompt forbade it.

## Limitations

- **One run per experiment.** The bot and the judge are non-deterministic, so a one-case difference between runs is not evidence by itself. The improvement for #5 and #8 is supported by the traces, not by the score difference alone.
- **The judge is not calibrated.** Bot (`claude-haiku-4-5`) and judge (`claude-sonnet-5`) are from the same vendor. I reviewed the failing verdicts (#4, #5, #8, #2) against the traces, and I agreed with them. I did not review the passing verdicts, so false passes are not ruled out.
- **UI averages can lag.** The averages shown in the LangSmith UI can be stale while evaluator results are still arriving. Reload the page before reading them; this README reports counts out of 12.
- **The retriever is a teaching tool.** Plural handling is a one-rule heuristic ("does" becomes "doe", consistently on both sides, so matching still works). Words with different forms ("fee" vs "fees" works, "pay" vs "payment" does not) will still miss. Tie-breaking between equal scores follows document load order. Embedding search would remove these bugs and add others (see the T22.5 project in this portfolio).
- **12 cases is small.** Each failure mode has one to three cases.
- **The judge is not unit-tested** because it requires a live API call. Only the code evaluator and the retriever are covered by tests.
- **The baseline run cannot be reproduced from the current code** without removing `singular()` from `tokenize`.

## Security and privacy

- `.env` is gitignored. API keys are never printed or committed.
- LangSmith stores full inputs and outputs of every run. Dataset case #10 contains a well-known test card number to check that the bot does not repeat it. In production, customer messages would need redaction before tracing.

## Cost and latency

A full 12-case run costs about $0.006 to $0.007 for the bot plus the judge calls (not traced). Latency is dominated by the model call (about 1 second of the 1.2 s end-to-end), while `retrieve` and `build_context` take effectively 0 s on 10 chunks. The slowest cases are the ones with the longest answers, such as the lost-card steps (2.30 s in the baseline).

## Pinned dependencies

See `requirements.txt`. `anthropic<1` is pinned on purpose; see finding 1.