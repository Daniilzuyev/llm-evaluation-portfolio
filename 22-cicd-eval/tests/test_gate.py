from gate.check_scores import failed_scorers, THRESHOLDS


def test_gate_passes_on_normal_run():
    summary = {"comparison": {"scores": {"matches_expected": {"score": 0.9167}, "no_phone_number": {"score": 1.0}}}}
    assert failed_scorers(summary, THRESHOLDS, 12) == []

def test_gate_fails_when_judge_drops():
    summary = {"comparison": {"scores": {"matches_expected": {"score": 0.5833}, "no_phone_number": {"score": 1.0}}}}
    assert failed_scorers(summary, THRESHOLDS, 12) == ["matches_expected"]

def test_gate_passes_at_threshold():
    summary = {"comparison": {"scores": {"matches_expected": {"score": 0.6667}, "no_phone_number": {"score": 1.0}}}}
    assert failed_scorers(summary, THRESHOLDS, 12) == []

def test_gate_fails_on_one_phone_number():
    summary = {"comparison": {"scores": {"matches_expected": {"score": 0.9167}, "no_phone_number": {"score": 0.9167}}}}
    assert failed_scorers(summary, THRESHOLDS, 12) == ["no_phone_number"]