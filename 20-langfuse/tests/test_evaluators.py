from experiments.evaluators import no_phone_number

# Ответ с телефоном "Call 555-123-4567" даёт value == 0.
# Ответ без телефона "Your limit is $500." даёт value == 1.
def test_no_phone_number_flags_phone():
    result = no_phone_number(
        input={"query": "x"},
        output="Call 555-123-4567",
        expected_output=None,
        metadata=None,
    )
    assert result["value"] == 0

def test_no_phone_number_passes_clean_answer():
    result = no_phone_number(
        input={"query": "x"},
        output="Your limit is $500.",
        expected_output=None,
        metadata=None,
    )
    assert result["value"] == 1
