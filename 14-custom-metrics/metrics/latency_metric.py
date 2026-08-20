from metrics.base_metric import BaseCustomMetric, MetricResult

class LatencyMetric(BaseCustomMetric):
    name = "latency_check"
    threshold = 1.0
    MAX_LATENCY_MS = 2000

    def measure(self, input_text, output_text, latency_ms, **kwargs) -> MetricResult:

        if latency_ms <= self.MAX_LATENCY_MS:
            score = 1.0
            reason = f"Latency {latency_ms} ms within limit ({self.MAX_LATENCY_MS} ms)"
        else:
            score = 0.0
            reason = f"Latency {latency_ms} ms exceeds limit ({self.MAX_LATENCY_MS} ms)"
        passed = score >= self.threshold

        return MetricResult(name=self.name, score=score, reason=reason, passed=passed, latency_ms=latency_ms)

