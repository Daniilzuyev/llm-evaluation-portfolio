import asyncio
import json
from src.claude_client import ClaudeClient


def main():
    client = ClaudeClient()

    print("=" * 60)
    print("1. Single Response Evaluation")
    print("=" * 60)

    result = client.evaluate_quality(
        prompt="What is test automation?",
        response="Test automation is writing scripts to run tests automatically."
    )
    print(f"Score: {result['score']}")
    print(f"Reasoning: {result['reasoning'][:150]}...\n")

    print("=" * 60)
    print("2. Compare Two Responses")
    print("=" * 60)

    comparison = client.compare_responses(
        prompt="What is CI/CD?",
        response_a="CI/CD automates deployment.",
        response_b="Continuous Integration and Continuous Delivery is a practice where code changes are automatically built, tested, and deployed."
    )
    print(f"Winner: {comparison['winner']}")
    print(f"Score A: {comparison['scores']['A']}")
    print(f"Score B: {comparison['scores']['B']}")
    print(f"Reasoning: {comparison['reasoning'][:150]}...\n")

    print("=" * 60)
    print("3. Batch Evaluation (3 test cases)")
    print("=" * 60)

    with open('data/eval_test_cases.json', 'r') as f:
        test_cases = json.load(f)

    results = asyncio.run(client.batch_evaluate(test_cases))

    for i, result in enumerate(results, 1):
        print(f"\nCase {i}:")
        print(f"  Prompt: {result['prompt']}")
        print(f"  Score: {result['score']}")
        print(f"  Reasoning: {result['reasoning'][:100]}...")


if __name__ == "__main__":
    main()