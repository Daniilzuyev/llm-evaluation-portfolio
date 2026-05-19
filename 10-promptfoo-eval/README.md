# T16 — PromptFoo Eval

## Scenarios
- **Classifier** — bug severity classification (critical/high/low)
- **Extractor** — structured data extraction from bug reports (JSON)
- **Summarizer** — pull request description summarization
- **RAG Q&A** — context-based Q&A with hallucination prevention

## Run
```bash
npx promptfoo@latest eval -c configs/classifier.yaml
npx promptfoo@latest eval -c configs/extractor.yaml
npx promptfoo@latest eval -c configs/summarizer.yaml
npx promptfoo@latest eval -c configs/rag_qa.yaml
```

## Key Findings
- v1 (rules-based) vs v2 (few-shot) comparison across all scenarios
- Classifier: v1 provided better result, because v2 was failed on "Password reset email" was classified as critical instead of high
- Extractor: start was 60%, finish 100% after prompt's iteration. V2 returned extra fields (issue, load_time) and unused before severity (moderate, minor) - no strong rules
- Summarizer: v2 has provided more detailed results - few-shot example provided correct format. V1 added extra text ("enhance user experience")
- RAG Q&A: tested not only correct answers and model say "I don't know" as a result it's provide safety from hallucination