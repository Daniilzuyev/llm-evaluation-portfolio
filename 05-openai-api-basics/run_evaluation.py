from llm_tester import LLMTester
import json

with open("test_cases.json") as f:
    test_cases = json.load(f)

tester = LLMTester(model="gpt-4o-mini")
results = tester.test_batch(test_cases)

print("=== BATCH TEST RESULTS ===")
print(results)
print("\n=== SUMMARY ===")
print(f"Total tests: {len(results)}")
print(f"Passed: {results['passed'].sum()}")
print(f"Failed: {(~results['passed']).sum()}")
print(f"Total cost: ${results['cost_usd'].sum():.6f}")
print(f"Average time: {results['response_time'].mean():.2f}s")

results.to_csv("results.csv", index=False)
print("\nResults saved to results.csv")