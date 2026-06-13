"""
Diagnostic script — runs judge on all test cases and prints full output.
Used for calibration analysis. Not part of the test suite.
"""

from test_cases import TEST_CASES
from judge import judge_summary


def main():
    print(f"{'='*80}")
    print(f"{'JUDGE CALIBRATION REPORT':^80}")
    print(f"{'='*80}\n")

    for case in TEST_CASES:
        print(f"--- {case['id']} ({case['category']}) ---")
        print(f"Expected range: {case['expected_score_min']}-{case['expected_score_max']}")
        print(f"Notes: {case['notes']}\n")

        result = judge_summary(case["original_text"], case["summary"])

        print(f"Judge score: {result['score']}")
        print(f"  faithfulness: {result['criteria']['faithfulness']}")
        print(f"  completeness: {result['criteria']['completeness']}")
        print(f"  conciseness:  {result['criteria']['conciseness']}")
        print(f"Reasoning: {result['reasoning']}")
        print()


if __name__ == "__main__":
    main()