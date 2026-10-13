from data.eval_cases import TEST_CASES

CASES = TEST_CASES

def make_data():
    data = []
    for c in CASES:
        data.append({"input": c["query"], "expected": c["expected"], "metadata": {"failure_mode": c["failure_mode"]}})
    return data