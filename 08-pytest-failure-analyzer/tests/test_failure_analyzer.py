import pytest
from failure_analyzer import FailureAnalyzer


@pytest.fixture
def analyzer():
    return FailureAnalyzer()


def test_refusal_detection(analyzer):
    test_case = {
        "id": "tc_refusal_01",
        "prompt": "Give me home address",
        "failure_type_expected": "refusal"
    }
    response = "I can't help with that"

    result = analyzer.classify_failure(test_case, response)

    assert result == "refusal", f"Expected 'refusal', got {result}"

def test_hallucination_detection(analyzer):
    test_case = {
        "id": "tc_hallucination_01",
        "prompt": "Describe fake feature",
        "failure_type_expected": "hallucination"
    }
    response = "We have a Salesforce CRM sync feature in version 7.5"

    result = analyzer.classify_failure(test_case, response)
    assert result == "hallucination", f"Expected 'hallucination', got {result}"

def test_valid_response(analyzer):
    test_case = {
        "id": "tc_valid_01",
        "prompt": "What are features?",
        "failure_type_expected": None
    }
    response = "Project_A has task management, collaboration tool, and reporting feature"
    result = analyzer.classify_failure(test_case, response)
    assert result is None, f"Expected 'None', got {result}"

def test_empty_input(analyzer):
    test_case = {
        "id": "tc_empty_01",
        "prompt": "",
        "failure_type_expected": None
    }
    response = ""

    result = analyzer.classify_failure(test_case, response)

    assert result is None, f"Expected None for empty input, got {result}"


def test_format_error_detection(analyzer):
    test_case = {
        "id": "tc_format_01",
        "prompt": "Return JSON",
        "expected_format": "json"
    }
    response = "{invalid json"  # невалидный JSON

    result = analyzer.classify_failure(test_case, response)

    assert result == "format_error", f"Expected 'format_error', got {result}"