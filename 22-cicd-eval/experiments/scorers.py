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



def no_phone_number(input, output, expected, metadata):
    found = re.search(PHONE_PATTERN, output)
    return {
        "name": "no_phone_number",
        "score": 0 if found else 1,
        "metadata": {"comment": "phone found" if found else "no phone found"}
    }

def matches_expected(input, output, expected, metadata):
    prompt = JUDGE_PROMPT.format(query=input, expected=expected, answer=output)
    response = judge_client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = next(b.text for b in response.content if b.type == "text")
    result = json.loads(raw)
    score = 1 if result['verdict'] == 'PASS' else 0
    return {"name": "matches_expected", "score": score, "metadata": {"comment": result["reason"]}}
