# 18-rag-hands-on — RAG with LangChain + ChromaDB, evaluated with RAGAS

Rebuild of the T22 RAG pipeline (`17-rag-eval`) with **embedding-based retrieval**
(ChromaDB) and **LangChain** orchestration, evaluated with the same RAGAS setup.

**Goal:** measure what changes when only the retriever changes —
keyword matching (T22) vs. embedding search (T22.5) — on the same corpus,
the same test cases, the same judge, and the same thresholds.

---

## Why this project

T22 used a hand-written keyword retriever. It worked, but two real bugs were
found on live data (stopwords counted as matches; `"us"` matching inside
`"Unused"`). Keyword matching also misses paraphrased questions entirely.

Production RAG systems almost always use embedding search and a vector
database. This project answers two practical questions:

1. Does embedding retrieval improve RAGAS scores on the same data?
2. What new failure modes does it introduce?

---

## Architecture

```
18-rag-hands-on/
├── data/
│   ├── hr_docs/              # 4 mock HR policy docs (.md + YAML front matter), same as T22
│   └── test_cases.py         # 14 test cases (FM1–FM7), same as T22
├── rag_system/
│   ├── vectorstore.py        # load docs → chunk → LangChain Documents → build Chroma index
│   ├── retriever.py          # similarity search over the Chroma index (top-k=3)
│   ├── generator.py          # context building + answer generation via ChatAnthropic
│   └── chain.py              # retrieve → build context → generate, returns RAGResult
├── evaluation/
│   ├── config.py             # RAGAS judge LLM + judge embeddings
│   ├── ragas_eval.py         # runs 6 RAGAS cases through the new pipeline, scores 4 metrics
│   └── report.py             # thresholds, per-case pass/fail, summary stats
└── chroma_db/                # generated index (gitignored)
```

### Pipeline flow

```
query
  → retrieve()          Chroma finds the 3 chunks closest in meaning to the query
  → build_context()     joins the 3 chunks into one text block
  → generate_answer()   Claude answers using ONLY that context
  → RAGResult(query, answer, retrieved_contexts)
```

### Models

| Role | Model |
|---|---|
| Generation | `claude-haiku-4-5` (via `langchain_anthropic.ChatAnthropic`) |
| Retrieval embeddings | `langchain_openai.OpenAIEmbeddings` |
| RAGAS judge | `claude-sonnet-5` |
| RAGAS judge embeddings | `text-embedding-3-small` (via `ragas.embeddings.OpenAIEmbeddings`) |

Anthropic has no embeddings API, so OpenAI is used for embeddings.
Two different `OpenAIEmbeddings` classes are needed (LangChain's for Chroma,
RAGAS's for the judge) and are imported under different names to avoid a
silent name collision.

---

## How to run

```powershell
py -m pip install -r requirements.txt
```

Create `.env` in the project root:

```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

Run from the project root (not by running files directly, to avoid `ModuleNotFoundError`):

```powershell
py -m rag_system.vectorstore     # 1. build the index (once)
py -m rag_system.chain           # 2. smoke test: one query end-to-end
py -m evaluation.report          # 3. full RAGAS eval + pass/fail report
```

**Rebuilding the index:** delete `chroma_db/` first. `Chroma.from_documents()`
appends to an existing collection, so re-running step 1 without deleting it
indexes every chunk a second time.

---

## Results: T22 (keyword retrieval) vs T22.5 (embedding retrieval)

Same corpus (4 HR docs, 10 chunks), same 6 RAGAS test cases (FM1/FM2/FM4),
same judge (`claude-sonnet-5`), same thresholds. Only the retriever changed.

### Summary

| | T22 (keyword) | T22.5 (embedding) |
|---|---|---|
| Cases passed | 1/6 | 2/6 |

Per-case T22 scores: see [`17-rag-eval`](../17-rag-eval/README.md).

### Per-case scores (T22.5, final run)

| case_id | faithfulness | answer_relevancy | context_precision | context_recall | passed |
|---|---|---|---|---|---|
| fm1_a | 0.75 | 0.00 | 0.00 | 1.00 | ❌ |
| fm1_b | 0.67 | 0.00 | 0.00 | 1.00 | ❌ |
| fm2_a | 1.00 | 0.97 | 1.00 | 1.00 | ✅ |
| fm2_b | 1.00 | 0.99 | 1.00 | 1.00 | ✅ |
| fm4_a | 0.71 | 0.93 | 0.00 | 0.50 | ❌ |
| fm4_b | 0.67 | 1.00 | 0.00 | 0.50 | ❌ |

**Thresholds:** faithfulness ≥ 0.7, answer_relevancy ≥ 0.5,
context_precision ≥ 0.3, context_recall ≥ 0.5 (carried over from T22, not recalibrated).

**Note on non-determinism:** faithfulness varied between runs on identical input
(e.g. `fm1_a`: 0.8 → 1.0 → 0.25 → 0.75 across 4 runs). The judge runs without
temperature control (see T21). Treat single-run faithfulness scores as unstable.

---

## Key findings

**1. The two T22 retriever bugs are structurally impossible here.**
T22's keyword retriever had two bugs found on live data: stopwords ("how",
"do", "the") counted as matches, and `"us"` substring-matched inside
`"Unused"`. Embedding retrieval compares meaning, not letters, so neither
bug can occur. This is a change of mechanism, not a patch.

**2. Embedding retrieval introduced a new failure: topically similar but wrong chunks.**
For "how many vacation days in the US?", the top-3 retrieved chunks were:
US vacation policy (correct), EU vacation policy (same topic, wrong
jurisdiction), flu/sick leave (irrelevant). Embeddings capture *topic* well
but don't treat "US" as a hard filter. This is the most likely driver of
`context_precision = 0.0` on 4/6 cases.

**Structural fix (not implemented):** filter by jurisdiction metadata before
similarity search, or keep jurisdiction-specific documents separate and
route by detected location.

**3. `answer_relevancy = 0.0` on FM1 is a metric limitation, not a bot failure.**
Both FM1 queries are jurisdiction-ambiguous ("how many vacation days do I have?").
The bot correctly asked which office the user is in and listed both values
(US: 15, EU: 25) instead of guessing. RAGAS AnswerRelevancy flags this as
"noncommittal" and zeroes the score. Same pattern observed in T22.
For jurisdiction-ambiguous queries, a clarifying question is the correct
answer. This needs a custom metric (see T22's `JurisdictionMetric`), not
a lower threshold.

**4. Results are not stable across runs.**
On a 5th run, `fm4_b` context_recall dropped 0.5 → 0.2 and `fm1_a`
faithfulness moved to 0.78, with no code changes. With 6 cases, a single
run is not enough to claim T22.5 is better than T22. The 1/6 → 2/6
improvement is directional, not proven.

---

## When to use which retriever

| | Hand-written keyword (T22) | LangChain + Chroma embeddings (T22.5) |
|---|---|---|
| Paraphrased questions | Missed | Found |
| Exact terms (IDs, country codes, "US" vs "EU") | Strong | Weak without metadata filters |
| Debuggability | Every scoring step visible | Search logic hidden inside Chroma |
| Extra dependencies | None | Embeddings provider + vector DB |
| Cost per query | Zero | One embeddings API call |
| Code to write | More | Less |

In practice, production systems often combine both (keyword + embedding
search, then metadata filtering). This project isolates each approach to
see its failure modes clearly.

---

## Cost / latency

A full eval run (6 cases) takes ~22–31 seconds. Each case makes one
generation call plus 4 judge calls (one per RAGAS metric), plus embeddings
calls for retrieval and AnswerRelevancy. The vector index is built once and
reused, so no re-embedding of the corpus happens during eval.

---

## Security note

The installed `chromadb==1.5.9` is affected by CVE-2026-45829 (CVSS 10.0,
pre-auth remote code execution). As of September 2026 there is no patched
release on PyPI. The fix is merged upstream but not yet released.

The vulnerable path is the Python FastAPI Chroma server
(`/api/v2/.../collections` endpoint with `trust_remote_code=true`).
This project uses Chroma in **embedded mode only** (local `chroma_db/`
folder via `langchain_chroma`, no server, no `trust_remote_code`), so that
path is not reachable.

Do not run this setup as a network-exposed Chroma server until a patched
release ships.

---

## Limitations

- **Only 6 of 14 test cases evaluated.** Only FM1/FM2/FM4 have reference
  answers for RAGAS. FM5–FM7 custom metrics from T22 were not re-run on the
  new pipeline.
- **Small corpus (10 chunks).** With `k=3`, retrieval often has to include an
  irrelevant third chunk because fewer than 3 relevant chunks exist.
- **Thresholds not recalibrated.** Carried over from T22 to keep the
  comparison fair; not tuned against T22.5 score distributions.
- **No metadata filtering.** Jurisdiction is not stored or used as a filter,
  which directly causes finding #2.
- **Single-run results.** See finding #4.
- **`MetricResult.reason` is always `None`** in `ragas==0.4.3` (same as T21/T22).
- **Pydantic V1 warning on Python 3.14** from `langchain_core` — harmless,
  printed on every run.