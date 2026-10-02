from dotenv import load_dotenv

load_dotenv()

import anthropic
from langsmith import traceable
from langsmith.wrappers import wrap_anthropic

client = wrap_anthropic(anthropic.Anthropic())

@traceable
def answer_questions(question: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=200,
        system="You are a support assistant for Imagine Bank. Answer in 1-2 sentences",
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

if __name__ == "__main__":
    print(answer_questions("What is the monthly fee for a credit card?"))
    print(answer_questions("What is my daily transfer limit?"))