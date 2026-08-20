from metrics.base_metric import BaseCustomMetric, MetricResult


class CostMetric(BaseCustomMetric):
    name = "cost_check"
    threshold = 1
    MAX_COST_USD = 0.01

    def measure(self,input_text, output_text, token_count, cost_usd, **kwargs) -> MetricResult:

        if cost_usd <= self.MAX_COST_USD:
            score = 1.0
            reason = f"Cost {cost_usd} is less or equal than ({self.MAX_COST_USD} USD)"
        else:
            score = 0.0
            reason = f"Cost {cost_usd} is bigger or equal than ({self.MAX_COST_USD} USD)"
        passed = score >= self.threshold


        return MetricResult(name=self.name, score=score, cost_usd=cost_usd, passed=passed, reason=reason, token_count=token_count)