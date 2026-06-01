from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric
from llm_client import get_response

def test_answer_relevancy():
    actual_output = get_response("What are your business hours?")
    test_case = LLMTestCase(
        input="What are your business hours?",
        actual_output=actual_output
)
    metric = AnswerRelevancyMetric(threshold=0.7)
    assert_test(test_case, [metric])


