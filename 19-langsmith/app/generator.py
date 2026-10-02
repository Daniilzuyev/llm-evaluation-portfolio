from app.retriever import retrieve
from app.corpus import Chunk, load_chunks
from dotenv import load_dotenv
load_dotenv()
from langsmith import traceable


import anthropic
from langsmith.wrappers import wrap_anthropic

client = wrap_anthropic(anthropic.Anthropic())

SYSTEM_PROMPT = ("You are a support assistant for Imagine Bank.\n"
                 "1. Answer only according to Context.\n"
                 "2. If Context has no answer or is empty, reply exactly: 'I don't have that information.'\n"
                 "3. Don't guess phone numbers, addresses and contacts.\n"
                 "4. Don't ask card number, PIN or personal data of clients.\n")

@traceable
def build_context(chunks: list[Chunk]) -> str:
    texts = [chunk.text for chunk in chunks]
    return "\n\n".join(texts)

def build_user_message(query: str, context: str) -> str:
    return f"""Context: {context}
Question: {query}"""

@traceable
def generate_answer(query: str, context: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(query, context)}]
    )
    return response.content[0].text

if __name__ == "__main__":
    chunks = load_chunks()
    for query in ["What is the monthly fee for a credit card?",
                  "What's the weather tomorrow?"]:
        context = build_context(retrieve(query, chunks))
        print(query)
        print(generate_answer(query, context))
        print()
