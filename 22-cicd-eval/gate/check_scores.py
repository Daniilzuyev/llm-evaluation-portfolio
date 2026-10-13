import json
import sys

THRESHOLDS = {"matches_expected": 8, "no_phone_number": 12}

def failed_scorers(summary, thresholds, n_cases):
    failed = []
    for name, result in summary["comparison"]["scores"].items():
        passed = round(result["score"] * n_cases)
        print(name, passed)
        if passed < thresholds[name]:
            failed.append(name)
    return failed

if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8-sig") as f:
        summary = json.load(f)

    failed = failed_scorers(summary, THRESHOLDS, 12)
    print("failed:", failed)
    if failed:
        sys.exit(1)
