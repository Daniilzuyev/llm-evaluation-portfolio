# OpenAI API Basics: LLM Evaluation Toolkit

A foundational project for testing Large Language Models (LLMs) using OpenAI's API. This toolkit demonstrates keyword-based evaluation of LLM responses — a baseline approach used in production AI systems before implementing more sophisticated metrics.

## What This Does

- **Single test execution**: Test individual prompts with automatic keyword validation
- **Batch testing**: Run multiple test cases and generate performance reports
- **Cost tracking**: Calculate exact API costs per test and per batch
- **Response metrics**: Measure tokens used, response time, and pass/fail status

Built for workforce management customer support scenarios (scheduling conflicts, timesheet corrections, absence requests, report exports, login issues).

## Tech Stack

- Python 3.10+
- OpenAI API (gpt-4o-mini)
- pandas (results analysis)
- python-dotenv (environment management)

## Setup

1. **Clone and navigate:**
```bash
cd 05-openai-api-basics
```

2. **Create virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```

3. **Install dependencies:**
```bash
pip install openai pandas python-dotenv
```

4. **Configure API key:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

Get your API key from: https://platform.openai.com/api-keys

## Usage

### Single Test
```python
from llm_tester import LLMTester

tester = LLMTester(model="gpt-4o-mini")

result = tester.test_single(
    system_prompt="You are a customer support agent for a workforce management platform",
    user_message="How do I correct a timesheet?",
    expected_keywords=["edit", "timesheet", "manager"],
    temperature=0.0
)

print(f"Passed: {result['passed']}")
print(f"Cost: ${result['cost_usd']:.6f}")
```

### Batch Testing
```python
python run_evaluation.py
```

**Output:**
```
Total tests: 5
Passed: 3
Failed: 2
Total cost: $0.000762
Average time: 4.18s

Results saved to results.csv
```

## Results Format

| test_id | passed | input_tokens | output_tokens | total_tokens | cost_usd | response_time | answer |
|---------|--------|--------------|---------------|--------------|----------|---------------|--------|
| 1       | True   | 32           | 95            | 127          | 0.000062 | 3.8s          | There could be... |
| 2       | False  | 28           | 102           | 130          | 0.000065 | 4.2s          | To manually correct... |

## Project Structure
```
05-openai-api-basics/
├── llm_tester.py          # Core evaluation class
├── test_cases.json        # Test scenarios
├── run_evaluation.py      # Batch test runner
├── cost_calculator.py     # Standalone cost calculator
├── .env.example           # API key template
├── .gitignore
└── README.md
```

## Known Limitations

**Keyword-based validation has false negatives.** If the LLM uses synonyms (e.g., "modify" instead of "edit", "time record" instead of "timesheet"), the test fails even though the answer is semantically correct.

**Production alternative**: Use semantic similarity (sentence transformers, cosine similarity) or LLM-as-a-Judge patterns. These will be covered in later projects (deepeval, RAGAS).

## Cost Analysis

**Model**: gpt-4o-mini  
**Pricing** (March 2025):
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Typical test costs**:
- Single test: ~$0.00005 (0.005¢)
- 100-test batch: ~$0.005 (0.5¢)
- 1000-test batch: ~$0.05 (5¢)

## Author

Built as part of a structured curriculum: QA Engineer → LLM Evaluation Engineer transition.