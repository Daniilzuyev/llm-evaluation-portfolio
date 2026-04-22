def generate_report(results: list) -> str:
    total = len(results)
    matches = sum(1 for r in results if r['detected'] == r['expected'])
    accuracy = f"{matches / total:.0%}"
    return f"""FAILURE ANALYSIS REPORT
=======================
Total cases: {total}
Matches: {matches}
Accuracy: {accuracy}
"""