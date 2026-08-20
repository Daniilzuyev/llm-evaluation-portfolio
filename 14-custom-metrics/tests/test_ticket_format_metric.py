from metrics.ticket_format_metric import TicketFormatMetric

def test_ticket_found():
    m = TicketFormatMetric()
    result = m.measure("any", "Your request is registered as RE-231")
    assert result.passed is True
    assert result.score == 1.0

def test_ticket_not_found():
    m = TicketFormatMetric()
    result = m.measure("any", "Thanks for reaching out.")
    assert result.passed is False
    assert result.score == 0.0