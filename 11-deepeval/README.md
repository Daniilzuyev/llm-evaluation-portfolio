# 11-deepeval

Automated LLM evaluation pipeline using DeepEval and pytest. Tests a FAQ support bot across three quality dimensions: answer relevancy, toxicity, and custom behavioral criteria.

## Test Scenarios

| File | Metric | What it checks |
|------|--------|----------------|
| `test_answer_relevancy.py` | `AnswerRelevancyMetric` | Response is relevant to the user's question |
| `test_toxicity.py` | `ToxicityMetric` | Response contains no toxic or harmful content |
| `test_geval.py` | `GEval` | 10 scenarios: correctness, groundedness, conciseness, out-of-scope handling, prompt injection resistance, context conflict resolution |

## Tech Stack

- [DeepEval](https://github.com/confident-ai/deepeval) — LLM evaluation framework
- OpenAI `gpt-4o-mini` — tested model + LLM-as-Judge for GEval
- pytest — test runner

## Project Structure

```
11-deepeval/
├── .env                        # OPENAI_API_KEY (not committed)
├── requirements.txt
├── pytest.ini
├── conftest.py
├── llm_client.py               # OpenAI API wrapper
├── test_answer_relevancy.py    # Relevancy metric test
├── test_toxicity.py            # Toxicity metric test
└── test_geval.py               # GEval: 10 FAQ bot scenarios
```

## How to Run

```bash
pip install -r requirements.txt
```

Add your API key to `.env`:
```
OPENAI_API_KEY=your_key_here
```

Run all tests:
```bash
py -m pytest test_answer_relevancy.py test_toxicity.py test_geval.py -v
```

## Results

12 tests, 3 metrics, 0 failures.

GEval scenarios include edge cases: prompt injection resistance, context conflict resolution (conflicting docs with different dates), out-of-scope request handling, and multi-turn context simulation.