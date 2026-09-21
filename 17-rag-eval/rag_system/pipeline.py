from rag_system.retriever import Chunk, retrieve
from rag_system.generator import answer_generation
from dataclasses import dataclass

@dataclass
class RAGResult:
    query: str
    answer: str
    retrieved_contexts: list[str]
    retrieved_chunks: list[Chunk]

def run_pipeline(query: str, chunks: list[Chunk], top_k: int = 3) -> RAGResult:
    retrieved = retrieve(query, chunks, top_k=top_k)
    answer = answer_generation(query, retrieved)

    contexts = [chunk.text for chunk in retrieved]

    return RAGResult(
        query=query,
        answer=answer,
        retrieved_contexts=contexts,
        retrieved_chunks=retrieved
    )
