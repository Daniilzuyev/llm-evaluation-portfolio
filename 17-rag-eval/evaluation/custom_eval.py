from data.test_cases import TEST_CASES
from rag_system.corpus import load_corpus
from rag_system.retriever import chunk_corpus
from rag_system.pipeline import run_pipeline
from metrics.staleness_metric import StalenessMetric
from metrics.pii_leakage_metric import PIILeakageMetric
from metrics.jurisdiction_metric import JurisdictionMetric

def get_custom_cases():
    result = []
    for tc in TEST_CASES:
        if tc.reference is None:
            result.append(tc)
    return result

staleness_metric = StalenessMetric()
pii_metric = PIILeakageMetric()
jurisdiction_metric = JurisdictionMetric()

def run_custom_eval():
    docs = load_corpus()
    chunks = chunk_corpus(docs)
    custom_cases = get_custom_cases()

    results = []
    for tc in custom_cases:
        result = run_pipeline(tc.query, chunks)

        if tc.failure_mode == "FM5":
            metric_result = staleness_metric.measure(result.retrieved_chunks)
        elif tc.failure_mode == "FM6":
            metric_result = pii_metric.measure(query=tc.query, answer=result.answer)
        elif tc.failure_mode == "FM7":
            metric_result = jurisdiction_metric.measure(query=tc.query, answer=result.answer)
        else:
            metric_result = None   # FM3 — нет метрики, пропускаем пока

        results.append({
            "case_id": tc.id,
            "failure_mode": tc.failure_mode,
            "query": tc.query,
            "answer": result.answer,
            "metric_result": metric_result
        })

    return results