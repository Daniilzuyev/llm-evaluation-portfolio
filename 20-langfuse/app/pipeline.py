from dotenv import load_dotenv
load_dotenv()
from langfuse import observe

from app.corpus import load_chunks
from app.retriever import retrieve
from app.generator import build_context, generate_answer

CHUNKS = load_chunks()

@observe()
def answer_pipeline(query: str) -> str:
    found = retrieve(query, CHUNKS)
    context = build_context(found)
    return generate_answer(query, context)

if __name__ == "__main__":
    for query in ["What is the monthly fee for a credit card?",
                  "What's the weather tomorrow?"]:
        print(query)
        print(answer_pipeline(query))
        print()