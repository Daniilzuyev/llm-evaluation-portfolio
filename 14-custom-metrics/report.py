from metrics.cost_metric import CostMetric
from metrics.latency_metric import LatencyMetric
from metrics.ticket_format_metric import TicketFormatMetric

test_cases = [
    {
        "output_text": "Your request is registered as RE-4521.",
        "latency_ms": 1200,
        "cost_usd": 0.003,
        "token_count": 400,
    },
    {
        "output_text": "Thanks for reaching out, we'll get back to you.",
        "latency_ms": 2500,
        "cost_usd": 0.02,
        "token_count": 900,
    },
    {
        "output_text": "Ticket RE-1187 created for your issue.",
        "latency_ms": 800,
        "cost_usd": 0.001,
        "token_count": 150,
    },
]

metrics = [TicketFormatMetric(), LatencyMetric(), CostMetric()]

def run_all_metrics(test_case, metrics):
    result = []
    for metric in metrics:
        metric_result = metric.measure(input_text="", **test_case)
        result.append(metric_result)
    return result

def aggregate_results(all_results):
    summary = {}
    for result in all_results:
        if result.name not in summary:
            summary[result.name] = {"scores": [], "passed": 0, "failed": 0}
        summary[result.name]["scores"].append(result.score)
        if result.passed:
            summary[result.name]["passed"] += 1
        else:
            summary[result.name]["failed"] += 1

    for name in summary:
        scores = summary[name]["scores"]
        summary[name]["avg_score"] = sum(scores) / len(scores)

    return summary

if __name__ == "__main__":
    all_results = []
    for case in test_cases:
        results = run_all_metrics(case, metrics)
        all_results.extend(results)
    print(aggregate_results(all_results))


