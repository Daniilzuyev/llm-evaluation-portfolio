from metrics.base_metric import BaseCustomMetric, MetricResult
from datetime import date

class StalenessMetric(BaseCustomMetric):
    name = "staleness"
    threshold = 180  # days

    def measure(self, retrieved_chunks: list, **kwargs) -> MetricResult:
        today = date.today()
        stale_docs = []

        for chunk in retrieved_chunks:
            age_days = (today - chunk.doc_last_updated).days
            if age_days > self.threshold:
                stale_docs.append(chunk.doc_id)

        passed = not stale_docs
        score = 1.0 if passed else 0.0

        return MetricResult(
            name=self.name,
            score=score,
            passed=passed,
            reason=f"Stale documents used: {stale_docs}" if stale_docs else "All retrieved documents within freshness threshold"
        )