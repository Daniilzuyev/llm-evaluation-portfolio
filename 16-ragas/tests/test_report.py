from types import SimpleNamespace
from evaluation.report import evaluate_thresholds, THRESHOLDS, summarize


def test_evaluate_thresholds_all_pass():
    fake_result = SimpleNamespace(
        case_id="good_case",
        faithfulness=1.0,
        answer_relevancy=1.0,
        context_precision=1.0,
        context_recall=1.0,
    )
    report = evaluate_thresholds([fake_result])
    assert len(report) == 1
    assert report[0]['faithfulness_passed'] == True
    assert report[0]['answer_relevancy_passed'] == True
    assert report[0]['context_precision_passed'] == True
    assert report[0]['context_recall_passed'] == True

def test_evaluate_thresholds_all_fail():
    fake_result = SimpleNamespace(
        case_id="bad_case",
        faithfulness=0.0,
        answer_relevancy=0.0,
        context_precision=0.0,
        context_recall=0.0,
    )
    report = evaluate_thresholds([fake_result])
    assert len(report) == 1
    assert report[0]['faithfulness_passed'] == False
    assert report[0]['answer_relevancy_passed'] == False
    assert report[0]['context_precision_passed'] == False
    assert report[0]['context_recall_passed'] == False

def test_evaluate_thresholds_boundary():
    fake_result = SimpleNamespace(
        case_id="good_case",
        faithfulness=THRESHOLDS['faithfulness'],
        answer_relevancy=THRESHOLDS['answer_relevancy'],
        context_precision=THRESHOLDS['context_precision'],
        context_recall=THRESHOLDS['context_recall'],
    )
    report = evaluate_thresholds([fake_result])
    assert len(report) == 1
    assert report[0]['faithfulness_passed'] == True
    assert report[0]['answer_relevancy_passed'] == True
    assert report[0]['context_precision_passed'] == True
    assert report[0]['context_recall_passed'] == True

def test_summarisze_mixed():
    good_result = SimpleNamespace(case_id="good_case", faithfulness=1.0, answer_relevancy=1.0, context_precision=1.0, context_recall=1.0)
    bad_result = SimpleNamespace(case_id="bad_case", faithfulness=0.0, answer_relevancy=0.0, context_precision=0.0, context_recall=0.0)

    report = evaluate_thresholds([good_result, bad_result])
    summary = summarize(report)

    assert summary['faithfulness']['passed'] == 1
    assert summary['faithfulness']['total'] == 2

    assert summary['answer_relevancy']['passed'] == 1
    assert summary['answer_relevancy']['total'] == 2

    assert summary['context_precision']['passed'] == 1
    assert summary['context_precision']['total'] == 2

    assert summary['context_recall']['passed'] == 1
    assert summary['context_recall']['total'] == 2