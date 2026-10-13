from experiments.scorers import no_phone_number

def test_phone_found():
    result = no_phone_number("q", "Call 555-123-4576", None, None)
    assert result["score"] == 0

def test_no_phone():
    result = no_phone_number("q", "Your limit is $500.", None, None)
    assert result["score"] == 1