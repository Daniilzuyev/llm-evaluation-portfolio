"""
LLM-as-Judge for summarization quality evaluation.

Evaluates summaries against original text on 3 axes:
- Faithfulness: no hallucinated facts
- Completeness: key points covered
- Conciseness: no unnecessary verbosity

Returns a structured score (1-5) with per-criterion breakdown.
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Model used as judge. Different from typical "generator" models
# to avoid self-preference bias.
JUDGE_MODEL = 'claude-sonnet-4-20250514'

# Temperature MUST be 0 for deterministic, reproducible judging.
JUDGE_TEMPERATURE = 0

# Max tokens for judge response. JSON output is short, 500 is safe.
JUDGE_MAX_TOKENS = 500
client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

JUDGE_SYSTEM_PROMPT = """You are a strict evaluator of text summaries.

# Your task
You will receive an ORIGINAL TEXT and a SUMMARY of that text.
Your job is to evaluate the SUMMARY against the ORIGINAL TEXT. 

# Criteria
You must evaluate the summary on three independent axes:
- faithfulness: Does the summary contain ONLY facts present in the original text?
Penalize ANY information that is added, invented, distorted, or not directly
supported by the original — even if that information is true in real life.
- conciseness: Is the summary free from unnecessary repetition, filler phrases,
and verbose constructions? A concise summary delivers maximum information
density per word.
- completeness: Does the summary cover the key facts, events, and conclusions
  from the original text? Penalize summaries that omit major points or focus
  only on minor details while missing the main ideas.

# Scoring scale
Use a 1-5 integer scale for each criterion AND for the overall score:
5 - All criteria met: no hallucinations, no key facts missing, no fluff
4 - Minor issues: one small omission OR one minor reword that slightly changes meaning
3 - Noticeable problems: missing important point OR adds 1-2 unsupported details
2 - Serious problems: hallucinated facts OR misses majority of key points
1 - Unusable: fundamentally misrepresents the original OR fabricates most content

# Anti-bias rules
- The LENGTH of the summary is NOT a criterion by itself.
- Writing STYLE is NOT a criterion.
- Do NOT reward summaries that match your own writing style or vocabulary preferences.
  Evaluate ONLY against the original text, not against how you would write it.

# Output format
Return ONLY valid JSON in this exact schema. No markdown fences. No preamble.
{
  "score": <integer 1-5, the overall score>,
  "reasoning": "<one sentence explaining the overall score>",
  "criteria": {
    "faithfulness": <integer 1-5>,
    "conciseness": <integer 1-5>,
    "completeness": <integer 1-5>
  }
}
"""

def judge_summary(original_text: str, summary: str) -> dict:
    """
    Evaluate a summary against its original text using LLM-as-Judge.

    Args:
        original_text: The source text that was summarized.
        summary: The summary to evaluate.

    Returns:
        dict with keys: score (int 1-5), reasoning (str), criteria (dict).

    Raises:
        ValueError: if the judge response is not valid JSON.
    """
    user_message = f"ORIGINAL TEXT:\n{original_text}\n\nSUMMARY:\n{summary}"
    response = client.messages.create(model=JUDGE_MODEL,
                                      max_tokens=JUDGE_MAX_TOKENS,
                                      temperature=JUDGE_TEMPERATURE,
                                      system=JUDGE_SYSTEM_PROMPT,
                                      messages=[
                                          {"role": "user", "content": user_message}
                                      ])
    raw_text = response.content[0].text

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Judge returned invalid JSON: {raw_text}") from e

    return result