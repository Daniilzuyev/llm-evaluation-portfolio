from langchain_chroma import Chroma
from dataclasses import dataclass
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from rag_system.retriever import retrieve
from rag_system.generator import build_context, generate_answer
from dotenv import load_dotenv

load_dotenv()

@dataclass
class RAGResult:
    query: str
    answer: str
    retrieved_contexts: list[str]

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")

def run_pipeline(vectorstore: Chroma, query: str) -> RAGResult:
    retrieved = retrieve(vectorstore, query)
    build = build_context(retrieved)
    answer = generate_answer(query, build)
    contexts = [doc.page_content for doc in retrieved]
    return RAGResult(query, answer, contexts)

if __name__ == "__main__":
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=OpenAIEmbeddings()
    )
    result = run_pipeline(vectorstore, "how many vacation days in the US?")
    print(result.answer)
    print(result.retrieved_contexts)