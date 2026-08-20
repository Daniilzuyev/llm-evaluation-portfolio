from dataclasses import dataclass
from typing import Optional

@dataclass
class MetricResult:
    name: str
    score: float
    passed: bool
    reason: str
    latency_ms: Optional[float] = None
    token_count:Optional[int] = None
    cost_usd: Optional[float] = None

class BaseCustomMetric:
    name: str = "base_metric"
    threshold: float = 0.5

    def measure(self, input_text: str, output_text: str, **kwargs) -> MetricResult:
        raise NotImplementedError()
