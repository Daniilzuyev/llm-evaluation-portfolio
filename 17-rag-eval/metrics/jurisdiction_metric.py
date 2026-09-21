# metrics/jurisdiction_metric.py
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from metrics.base_metric import BaseCustomMetric, MetricResult

load_dotenv()

JURISDICTION_JUDGE_PROMPT = """You are evaluating whether an AI assistant correctly handled a jurisdiction-ambiguous question.

The company has multiple offices with different policies (e.g. different vacation day entitlements per country). The user's question does not specify which office/country they are in.

Original question: {query}
Assistant's response: {answer}

Did the assistant ask a clarifying question about which country/office applies, OR explicitly state that the answer depends on jurisdiction and list the relevant options?
Answer with ONLY "CLARIFIED" (asked or listed options) or "ASSUMED" (answered with one jurisdiction's policy without checking).

Respond with a single word only."""

judge_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
JUDGE_MODEL = "claude-sonnet-5"

def judge_jurisdiction(query: str, answer: str) -> str:
    prompt = JURISDICTION_JUDGE_PROMPT.format(query=query, answer=answer)
    response = judge_client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}]
    )
    verdict = response.content[0].text.strip().upper()
    return verdict

class JurisdictionMetric(BaseCustomMetric):
    name = "jurisdiction"
    threshold = 1.0

    def measure(self, query: str, answer: str, **kwargs) -> MetricResult:
        verdict = judge_jurisdiction(query, answer)
        passed = verdict == "CLARIFIED"
        score = 1.0 if passed else 0.0

        return MetricResult(
            name=self.name,
            score=score,
            passed=passed,
            reason=f"Judge verdict: {verdict}"
        )