THRESHOLDS = {
    'faithfulness': 0.5,
    'answer_relevancy': 0.59,
    'context_precision': 0.99,
    'context_recall': 0.99,
}

def evaluate_thresholds(results: list) -> list[dict]:
    reports = []
    for result in results:
        reports.append({
            'case_id': result.case_id,
            'faithfulness_passed': result.faithfulness >= THRESHOLDS['faithfulness'],
            'answer_relevancy_passed': result.answer_relevancy >= THRESHOLDS['answer_relevancy'],
            'context_precision_passed': result.context_precision >= THRESHOLDS['context_precision'],
            'context_recall_passed': result.context_recall >= THRESHOLDS['context_recall'],
        })
    return reports

def summarize(threshold_report: list[dict]) -> dict:
    summary = {}
    for metric in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        passed_count = sum(1 for row in threshold_report if row[f"{metric}_passed"])
        summary[metric] = {
            "passed": passed_count,
            "total": len(threshold_report),
        }
    return summary

