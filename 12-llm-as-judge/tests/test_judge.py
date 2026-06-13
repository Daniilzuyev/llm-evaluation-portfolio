"""
Tests for the LLM-as-Judge summarization evaluator.

Each test case from test_cases.py is run as a separate parametrized test.
Tests are marked with @pytest.mark.judge - they call the real Anthropic API and cost tokens.
"""
import pytest
from judge import judge_summary
from test_cases import TEST_CASES

# ─── Test 1: judge returns valid structure ───
@pytest.mark.judge
@pytest.mark.parametrize("case", TEST_CASES, ids = [c["id"] for c in TEST_CASES])
def test_judge_return_valid_structure(case):
    """Judge must return a dict with all required keys."""
    result = judge_summary(case['original_text'], case['summary'])

    # Top-level keys
    assert "score" in result
    assert "reasoning" in result
    assert "criteria" in result

    # Score is int 1-5
    assert isinstance(result['score'], int)
    assert 1 <= result['score'] <= 5

    # All 3 criteria present:
    assert "faithfulness" in result['criteria']
    assert "completeness" in result['criteria']
    assert "conciseness" in result['criteria']

# ─── Test 2: judge score matches expected range ───
@pytest.mark.judge
@pytest.mark.parametrize("case", TEST_CASES, ids=[c["id"] for c in TEST_CASES])
def test_judge_score_in_expected_range(case):
    """Judge's overall score must fall within expected min/max"""
    result = judge_summary(case['original_text'], case['summary'])

    score = result['score']
    min_score = case['expected_score_min']
    max_score = case['expected_score_max']

    assert min_score <= score <= max_score, (
        f"{case['id']}: expected {min_score}-{max_score}, got {score}. "
        f"Reasoning: {result['reasoning']}"
    )