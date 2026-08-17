# 13 — Red Teaming Engine with LLM-as-Judge

MC-1 mini-challenge (independent build, no scaffolding). Extends 
`09-red-teaming-engine`: keyword-based detector replaced with LLM-as-Judge.

## Why

Keyword matching (`if "leaked" in response`) misses semantic attacks and 
produces false positives/negatives — a known limitation of rule-based 
detection compared to semantic evaluation. LLM-as-Judge reads attack prompt 
+ victim rules + response together and reasons about actual failure, not 
string presence.

## Structure

- `core/detector.py` — `judge_attack(prompt, output, victim_rules) -> dict`. 
  One universal judge prompt for all attack categories. Strips markdown 
  fences before `json.loads()`. Handles model refusals explicitly 
  (`attack_success: None` instead of crash).
- `core/base_attack.py` — `BaseAttack`. `run()` calls the victim model, 
  then `judge_attack()` directly. No `evaluate()` — removed, added no value.
- `attacks/` — `Privacy`, `BiasFairness`, `InstructionFollowing`. Each is 
  just `name` + `prompts`, no logic — everything inherited from `run()`.
- `run_tests.py` — runner, aggregates results.

## Findings

- Victim model defended all three categories — no leaks, no biased reasoning.
- First version of the "Instruction Following" rule (max 3 sentences) caused 
  false positives: correct, well-explained refusals got flagged as attack 
  success just for being long. Relaxed to "concise, ~5 sentences" — 
  fewer false positives, still measurable.
- One attack (Base64-encoded payload) triggered a real judge refusal 
  (category: `bio`). Handled via explicit `stop_reason` check in 
  `judge_attack()`.

## Known gaps

- `attack_success: None` not aggregated separately in reporting yet.
- Judge prompt is universal, not per-category (simplicity over specificity, 
  intentional trade-off for MC-1).

## Run

py -m venv venv
venv\Scripts\activate
pip install anthropic python-dotenv
py run_tests.py