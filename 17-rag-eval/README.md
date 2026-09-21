# RAG Architecture & Evaluation
 
End-to-end RAG pipeline (retrieval + generation) built from scratch, evaluated
against the 7 failure modes designed in `eval-design.md`, using a mix
of RAGAS metrics (for failure modes with a text reference) and custom
metrics (for failure modes that are structural/behavioral, not text-quality
checks).
 
**Repo note:** `test-design/eval-design.md` is the design document that
precedes this code — see that file for the full failure-mode rationale,
metric mapping, and threshold-calibration methodology this implementation
follows.
 
---
 
## Problem Solved
 
An earlier RAGAS project (`16-ragas`) built a RAGAS evaluation pipeline
against a hand-crafted, static QA dataset — useful for learning the RAGAS
API, but not a real RAG system. This project closes that gap: a real
(simplified) retrieval + generation pipeline that produces its own answers
and contexts, evaluated end-to-end against all 7 failure modes from the
design doc — not just the 4 that RAGAS covers.
 
---
 
## Architecture
 
```
rag_system/
├── corpus.py        — loads .md documents with YAML front matter (python-frontmatter)
├── retriever.py       — paragraph-based chunking + keyword-overlap retrieval
├── generator.py         — Anthropic SDK call (claude-haiku-4-5), context-grounded prompt
└── pipeline.py             — orchestrates retrieve() + generate() → RAGResult
 
data/
├── hr_docs/            — 4 mock HR documents (front matter: id, title, last_updated)
└── test_cases.py          — 14 test cases, 2 per failure mode (FM1–FM7)
 
metrics/
├── base_metric.py       — custom metric contract (BaseCustomMetric, MetricResult), reused across projects
├── staleness_metric.py    — FM5, pure structural (date comparison, no LLM)
├── pii_leakage_metric.py    — FM6, LLM-judge (claude-sonnet-5) + unused regex pre-filter
└── jurisdiction_metric.py      — FM7, LLM-judge (claude-sonnet-5)
 
evaluation/
├── config.py       — judge_llm / embeddings, reused from the RAGAS project (model bumped to claude-sonnet-5)
├── ragas_eval.py      — FM1/FM2/FM4 (cases with a reference), 4 RAGAS metrics
├── custom_eval.py        — FM5/FM6/FM7 (cases without a reference), routes by failure_mode
└── report.py                — evaluate_ragas_case(), calculate_stats(), build_report()
 
tests/
└── test_report.py    — 5 pytest tests on report logic only (SimpleNamespace, no live API)
```
 
**Why documents are hardcoded per-file, not database-backed:** this is a
known, documented simplification for a 4-document mock corpus. A production
system would load from Confluence/Notion/S3 with `last_updated` coming from
the source system's own metadata, not a manually-written front matter field
— deferred as out of scope for this project.
 
**Why chunking is paragraph-based, not recursive/semantic:** the 4 mock
documents are already written with paragraphs as intentional semantic units
(each illness in `sick_leave.md` is its own paragraph, specifically to make
FM4 — retrieval algorithm miss — testable). Recursive/semantic chunking is
the right tool for longer, real-world documents; introducing it here would
conflate two different techniques (RAG architecture vs. embeddings) in one
project. Semantic chunking is deferred to a follow-up project (ChromaDB + LangChain).
 
---
 
## Metric → Failure Mode Mapping
 
| FM | Failure Mode | Metric | Type | Reference needed? |
|----|---|---|---|---|
| 1 | Ungrounded Numeric Hallucination | Faithfulness | RAGAS | Yes |
| 2 | Topic Drift / Low Answer Relevancy | Answer Relevancy | RAGAS | Yes |
| 3 | Knowledge Base Content Gap | — | none (no automated check in this MVP) | — |
| 4 | Retrieval Algorithm Miss | Context Recall | RAGAS | Yes |
| 5 | Stale Document Retrieval | StalenessMetric | Custom, structural | No |
| 6 | PII / Confidentiality Leakage | PIILeakageMetric | Custom, LLM-judge | No |
| 7 | Jurisdiction/Location Mismatch | JurisdictionMetric | Custom, LLM-judge | No |
 
FM3 has no automated metric in this MVP — per the design doc, the correct
behavior ("list what exists, flag that the KB may not be exhaustive") is a
qualitative judgment call, not yet automated here. `data/test_cases.py`
still includes FM3 cases so they can be manually reviewed or automated
later.
 
---
 
## Real Findings (from actual runs, not theory)
 
**Retriever: two real bugs found and fixed on live data.**
- Naive keyword scoring counted stopwords ("how", "do", "the", "in") as
  matches regardless of topic — a sick-leave chunk outranked the correct
  vacation chunk purely on stopword overlap. Fixed by filtering a
  `STOP_WORDS` set before scoring.
- Substring matching caused `"us"` (from the query "...in the US?") to
  match inside `"Unused"` in the EU vacation document, giving `vacation_eu`
  a false-positive point and letting it tie/beat `vacation_us` in
  relevance. Fixed by comparing against whole, punctuation-stripped words
  (`word in chunk_words`) instead of substring containment
  (`word in chunk_text`).
**RAGAS scores are low across most FM1/FM2/FM4 cases — root-caused, not a
bug.** On a first full run, 5 of 6 RAGAS cases failed their thresholds.
Inspecting `fm1_b` directly showed why: `context_precision` and
`answer_relevancy` were near-zero because the top-3 retrieved chunks
included a third, irrelevant chunk (`interview_requirements` — QA hiring
criteria — retrieved for a vacation-days question) purely because the
10-chunk mock corpus doesn't always have 3 genuinely relevant chunks for
every query. This is a retrieval-layer limitation of the simple
keyword-based retriever on a small corpus, not a generation-layer failure —
documented here rather than silently accepted or hidden by loosening
thresholds to pass everything.
 
**A generation behavior surfaced that RAGAS wasn't designed to score.**
`fm1_b` ("What's my total vacation allowance?" — deliberately ambiguous on
jurisdiction) got a well-grounded, correct answer from the generator: it
asked which office the user was in, rather than guessing. This is exactly
the desired FM7 behavior — but the case is tagged FM1 in the test set, and
RAGAS's `AnswerRelevancy` metric (which checks whether the response
resembles a direct answer to the question) scored it `0.0`, because a
clarifying question isn't the same shape as a direct answer. This is a
genuine mismatch between what RAGAS measures and what "correct" looks like
for jurisdiction-ambiguous queries — worth flagging in future threshold
calibration rather than treating the `0.0` as a real generation failure.
 
**Version-compatibility fix reused from an earlier project, reapplied here.**
`ModuleNotFoundError: langchain_community.chat_models.vertexai` recurred in
this repo's environment (same root cause as before: the submodule was
removed from `langchain-community` after `ragas==0.4.3` shipped, but `ragas`
still imports it unconditionally). Fixed the same way — a one-line
re-export shim in `site-packages/langchain_community/chat_models/vertexai.py`
(`from langchain_google_vertexai import ChatVertexAI`), which required
installing `langchain-google-vertexai` as a new dependency in this
environment. **Confirmed: this fix does not persist across environments —
it must be reapplied per-venv/per-install, not just once globally.**
 
---
 
## Known Limitations / Scope Decisions (documented, not hidden)
 
- **PII regex pre-filter (`SALARY_PATTERN` in `pii_leakage_metric.py`) is
  defined but not wired into `measure()`.** The current implementation
  relies entirely on the LLM-judge layer. A production version would run
  the regex first as a cheap pre-filter (skip the LLM call entirely on
  obviously-clean answers) — deferred as a documented gap, not silently
  dropped.
- **`RAGAS_THRESHOLDS` are starting values, not calibrated against a real
  score distribution** (unlike the earlier RAGAS project, where thresholds
  were set after observing real score spread — see the design doc's
  calibration methodology). With only 6 RAGAS test cases here, there isn't
  yet enough data to calibrate meaningfully; `context_precision: 0.3` in
  particular was chosen deliberately low to avoid being meaningless given
  the known retrieval-noise issue above, not calibrated from a real gap in
  the data.
- **FM3 (Knowledge Base Content Gap) has no automated metric** — test cases
  exist but require manual review in this MVP.
- **Test data volume is 2 cases per failure mode (14 total), not the 5–8
  per failure mode (35–56 total) the design doc specifies** as the target
  for a fully calibrated eval set. This is a deliberate MVP scope decision —
  expanding case coverage is a natural follow-up, not a gap in the
  architecture itself.
---
 
## Running
 
```powershell
# smoke-test individual components
py -c "from rag_system.corpus import load_corpus; print(len(load_corpus()))"
 
# full RAGAS eval (6 cases, real API calls, ~30s)
py -m evaluation.ragas_eval
 
# full custom metrics eval (8 cases, real API calls for FM6/FM7 only)
py -c "from evaluation.custom_eval import run_custom_eval; print(run_custom_eval())"
 
# unified report (both layers combined)
py -c "from evaluation.report import build_report; print(build_report())"
 
# unit tests (report logic only, no live API, <0.1s)
py -m pytest tests/test_report.py -v
```