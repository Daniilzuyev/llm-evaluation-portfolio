import os
import json

from rag_system.retriever import Chunk
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
GENERATOR_MODEL = 'claude-haiku-4-5'

SYSTEM_PROMPT = """You are an HR policy assistant. Answer the user's question using ONLY the context provided below.
If the context doesn't contain enough information to answer, say so explicitly - do not guess or use outside knowledge.
Do not state any number, dates, or facts that are not present in context.

Context:
{context}"""

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def build_context(chunks: list[Chunk]) -> str:
    context = []
    for chunk in chunks:
        context.append(chunk.text)
    return "\n\n".join(context)

def answer_generation(query:str, retrieved_chunks: list[Chunk]) -> str:
    context = build_context(retrieved_chunks)
    system_prompt = SYSTEM_PROMPT.format(context=context)

    response = client.messages.create(
        model=GENERATOR_MODEL,
        max_tokens=500,
        system=system_prompt,
        messages=[
            {"role": "user", "content": query}
        ]
    )

    return response.content[0].text
