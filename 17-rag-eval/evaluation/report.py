

RAGAS_THRESHOLDS = {
    "faithfulness": 0.7,
    "answer_relevancy": 0.5,
    "context_precision": 0.3,
    "context_recall": 0.5,
}

def evaluation_ragas_case(result) -> dict:
    passed = (
        result.faithfulness >= RAGAS_THRESHOLDS["faithfulness"]
        and result.answer_relevancy >= RAGAS_THRESHOLDS["answer_relevancy"]
        and result.context_precision >= RAGAS_THRESHOLDS["context_precision"]
        and result.context_recall >= RAGAS_THRESHOLDS["context_recall"]
    )
    return {
        "case_id": result.case_id,
        "passed": passed,
        "faithfulness": result.faithfulness,
        "answer_relevancy": result.answer_relevancy,
        "context_precision": result.context_precision,
        "context_recall": result.context_recall,
    }

def calculate_stats(all_results: list[dict]) -> dict:
    total = len(all_results)
    passed_count = sum(1 for r in all_results if r["passed"])
    return {
        "total": total,
        "passed": passed_count,
        "failed": total - passed_count
    }

def build_report():
    from evaluation.ragas_eval import run_evaluate, dataset
    from evaluation.custom_eval import run_custom_eval
    import asyncio

    ragas_results_raw = asyncio.run(run_evaluate.arun(dataset))
    ragas_results = [evaluation_ragas_case(r) for r in ragas_results_raw]

    custom_results_raw = run_custom_eval()
    custom_results = []
    for r in custom_results_raw:
        if r["metric_result"] is not None:
            custom_results.append({
                "case_id": r["case_id"],
                "passed": r["metric_result"].passed,
                "failure_mode": r["failure_mode"]
            })

    all_results = ragas_results + custom_results
    stats = calculate_stats(all_results)

    return {
        **stats,
        "ragas_results": ragas_results,
        "custom_results": custom_results
    }