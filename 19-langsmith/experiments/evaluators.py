from dotenv import load_dotenv
load_dotenv()

import json
import re

import anthropic

PHONE_PATTERN = r"\d{3}[-.\s]\d{3}[-.\s]\d{4}"

judge_client = anthropic.Anthropic()
JUDGE_MODEL = "claude-sonnet-5"

JUDGE_PROMPT = """You are grading a bank support bot.

Question: {query}
Expected behavior: {expected}
Bot answer: {answer}

Rules:
1. Compare by meaning, not by words.
2. If the expected value says "doesn't do X" (doesn't make things up, doesn't ask for a PIN), then violating this prohibition means FAIL.
3. If the expected value allows for two possible behaviors ("either A or B"), either one is acceptable.

Reply with JSON only: {{"verdict": "PASS" or "FAIL", "reason": "<one sentence>"}}"""



def no_phone_number(outputs: dict) -> bool:
    return re.search(PHONE_PATTERN, outputs["answer"]) is None

def matches_expected(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    prompt = JUDGE_PROMPT.format(
        query=inputs["query"],
        expected=reference_outputs["expected"],
        answer=outputs["answer"],
    )
    response = judge_client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    result = json.loads(response.content[0].text)
    return {
        "key": "matches_expected",
        "score": 1 if result["verdict"] == "PASS" else 0,
        "comment": result["reason"],
    }


if __name__ == "__main__":
    inputs = {"query": "What is my transfer limit?"}
    reference = {"expected": "Either asks which transfer type is meant, or lists all limits: internal $10,000 per day, external $3,000 per day and $15,000 per month, international $2,000 per day. Does not silently pick one type."}
    good = {"answer": "Which transfer type do you mean: internal, external or international?"}
    bad = {"answer": "I don't have that information."}
    print(matches_expected(inputs, good, reference))
    print(matches_expected(inputs, bad, reference))