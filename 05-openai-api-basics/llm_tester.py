from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv
import time

load_dotenv()

class LLMTester:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        self.pricing = {
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4o": {"input": 2.50, "output": 10.00},
        }

    def calculate_cost(self, input_tokens, output_tokens):
        if self.model not in self.pricing:
            raise ValueError(f"Unknown model: {self.model}")

        input_cost = input_tokens * self.pricing[self.model]["input"] / 1_000_000
        output_cost = output_tokens * self.pricing[self.model]["output"] / 1_000_000
        return input_cost + output_cost

    def test_single(self, system_prompt: str, user_message: str, expected_keywords: list[str] | None = None, temperature: float = 0.0):
        start = time.time()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
        response = self.client.chat.completions.create(model = self.model, messages=messages, temperature=temperature)
        duration = time.time() - start

        answer = response.choices[0].message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        if expected_keywords:
            passed = all(keyword.lower() in answer.lower() for keyword in expected_keywords)
        else:
            passed = True

        cost = self.calculate_cost(input_tokens, output_tokens)

        return {
            "answer": answer,
            "passed": passed,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": cost,
            "response_time": duration
        }

    def test_batch(self, test_cases: list[dict]):
        result = []
        for test_case in test_cases:
            res = self.test_single(test_case["system_prompt"], test_case["user_message"], test_case["expected_keywords"])
            res["test_id"] = test_case["id"]
            result.append(res)
        return pd.DataFrame.from_records(result)


if __name__ == "__main__":
    tester = LLMTester(model="gpt-4o-mini")

    result = tester.test_single(
        system_prompt="You are a math tutor",
        user_message="What is 15% of 200?",
        expected_keywords=["30"],
        temperature=0.0
    )

    print("=== TEST RESULT ===")
    print(f"Passed: {result['passed']}")
    print(f"Answer: {result['answer']}")
    print(f"Tokens: {result['total_tokens']}")
    print(f"Cost: ${result['cost_usd']:.6f}")
    print(f"Time: {result['response_time']:.2f}s")