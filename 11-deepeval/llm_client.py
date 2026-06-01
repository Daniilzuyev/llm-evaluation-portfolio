import os
from dotenv import load_dotenv
from openai import OpenAI


def get_response(prompt: str) -> str:
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = "gpt-4o-mini"
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}])
    return response.choices[0].message.content

if __name__ == "__main__":
    print(get_response("What is the capital of France?"))
