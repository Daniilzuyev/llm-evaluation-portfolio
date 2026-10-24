from app.tools import get_card_fee, get_transfer_limit


def test_credit_card_returns_credit_fee():
    assert "monthly maintenance fee is $8" in get_card_fee.invoke({"card_type": "credit"})

def test_unknown_card_type_returns_not_found_message():
    assert get_card_fee.invoke({"card_type": "gold"}) == "No fee information for card type: gold"

def test_external_transfer_returns_external_limit():
    assert "$3,000 per day" in get_transfer_limit.invoke({"transfer_type": "external"})

def test_unknown_transfer_type_returns_not_found_message():
    assert get_transfer_limit.invoke({"transfer_type": "crypto"}) == "No limit information for transfer type: crypto"