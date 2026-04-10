import os
import asyncio
import json
from anthropic import Anthropic
from dotenv import load_dotenv


class ClaudeClient:
    def __init__(self):
        load_dotenv()
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"

    def evaluate_quality(
            self,
            prompt: str,
            response: str,
            criteria: str = 'accuracy, relevance, clarity'
    ) -> dict:
        system_prompt = (
            f"You are an expert LLM evaluator. "
            f"Rate the response quality from 0 to 10 based on: {criteria}. "
            f"Return ONLY a JSON object with two fields: score (float) and reasoning (string)."
        )
        user_message = f"Prompt: {prompt}\n\nResponse: {response}"

        try:
            message = self.client.messages.create(
                model = self.model,
                max_tokens=512,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            result = json.loads(message.content[0].text)
            return result

        except json.JSONDecodeError:
            return {"score": 0.0, "reasoning": "Failed to parse Claude Response"}

    def compare_responses(self, prompt: str, response_a: str, response_b: str) -> dict:
        system_prompt = (
            "You are an expert LLM evaluator. "
            "Compare two responses with same prompt. "
            "Determine which is better or if they're equal."
            "Return only a JSON object with three fields: "
            "winner (string A, B, or Tie), reasoning string, "
            "scores (object with A and B as floats from 0-10)."
        )

        user_message = (
            f"Prompt: {prompt}\n\n"
            f"Response A: {response_a}\n\n"
            f"Response B: {response_b}"
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=512,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            result = json.loads(message.content[0].text)
            return result
        except json.JSONDecodeError:
            return {
                "winner": "Tie",
                "reasoning": "Failed to parse Claude response",
                "score": {"A": 0.0, "B": 0.0}
            }

    async def batch_evaluate(self, test_cases: list[dict]) -> list[dict]:
        async def evaluate_single(case: dict) -> dict:
            result = await asyncio.to_thread(
                self.evaluate_quality,
                prompt = case['prompt'],
                response = case['response']
            )

            return {
                "prompt": case['prompt'],
                'response': case['response'],
                'score': result['score'],
                'reasoning': result['reasoning']
            }

        tasks = [evaluate_single(case) for case in test_cases]
        results = await asyncio.gather(*tasks)

        return results