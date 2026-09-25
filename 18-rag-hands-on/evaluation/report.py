

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

def calculate_stats(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    return {"total": total, "passed": passed, "failed": failed}

if __name__ == "__main__":
    from evaluation.ragas_eval import main
    import asyncio

    results = asyncio.run(main())
    evaluated = [evaluation_ragas_case(r) for r in results]
    stats = calculate_stats(evaluated)
    print(stats)
    for e in evaluated:
        print(e)
