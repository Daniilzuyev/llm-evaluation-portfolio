from types import SimpleNamespace
from evaluation.report import evaluation_ragas_case, calculate_stats


def test_evaluate_ragas_case_all_pass():
    fake_result = SimpleNamespace(
        case_id="test1",
        faithfulness=0.9,
        answer_relevancy=0.9,
        context_precision=0.9,
        context_recall=0.9,
    )
    result = evaluation_ragas_case(fake_result)
    assert result["passed"] is True

def test_evaluate_ragas_case_all_fail():
    fake_result = SimpleNamespace(
        case_id="test2",
        faithfulness=0.6,
        answer_relevancy=0.4,
        context_precision=0.2,
        context_recall=0.4,
    )
    result = evaluation_ragas_case(fake_result)
    assert result["passed"] is False

def test_evaluate_ragas_case_exact_threshold():
    fake_result = SimpleNamespace(
        case_id="test3",
        faithfulness=0.7,
        answer_relevancy=0.5,
        context_precision=0.3,
        context_recall=0.5
    )
    result = evaluation_ragas_case(fake_result)
    assert result["passed"] is True

def test_evaluate_ragas_case_partly_threshold():
    fake_result = SimpleNamespace(
        case_id="test4",
        faithfulness=0.7,
        answer_relevancy=0.5,
        context_precision=0.1,
        context_recall=0.5
    )
    result = evaluation_ragas_case(fake_result)
    assert result["passed"] is False

def test_calculate_stats():
    fake_results = [
        {"passed": True},
        {"passed": True},
        {"passed": False}
    ]
    stats = calculate_stats(fake_results)
    assert stats["total"] == 3
    assert stats["passed"] == 2
    assert stats["failed"] == 1