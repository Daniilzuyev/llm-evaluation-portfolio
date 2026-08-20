from metrics.base_metric import BaseCustomMetric, MetricResult
import re

class TicketFormatMetric(BaseCustomMetric):
    name = "ticket_format"
    threshold = 1

    def measure(self, input_text: str, output_text:str, **kwargs) -> MetricResult:
        match = re.search(r"RE-\d+", output_text)
        if match is not None:
            score = 1
        else:
            score = 0
        passed = score >= self.threshold

        if match is not None:
            reason = f"Ticket found: {match.group()}"
        else:
            reason = "No ticket ID found"

        return MetricResult(name = self.name, score = score, passed = passed, reason = reason)
