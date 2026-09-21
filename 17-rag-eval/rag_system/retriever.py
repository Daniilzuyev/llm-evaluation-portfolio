from dataclasses import dataclass
from rag_system.corpus import Document
import string

@dataclass
class Chunk:
    doc_id: str
    text: str
    doc_last_updated: str

STOP_WORDS = {
    "how", "what", "when", "where", "why", "who", "which",
    "do", "does", "did", "is", "are", "was", "were",
    "i", "you", "he", "she", "it", "we", "they",
    "the", "a", "an", "in", "on", "at", "to", "for", "of",
    "have", "has", "had", "can", "could", "will", "would",
    "my", "me", "this", "that", "these", "those"
}

def chunk_document(doc: Document) -> list[Chunk]:
    chunks = []
    paragraphs = doc.content.split("\n\n")
    for paragraph in paragraphs:
        cleaned = paragraph.strip()
        if cleaned:
            chunks.append(Chunk(
                doc_id=doc.id,
                text=cleaned,
                doc_last_updated=doc.last_updated
            ))
    return chunks

def chunk_corpus(documents: list[Document]) -> list[Chunk]:
    chunks = []
    for doc in documents:
        doc_chunks = chunk_document(doc)
        chunks.extend(doc_chunks)
    return chunks

def retrieve(query: str, chunks: list[Chunk], top_k: int = 3) -> list[Chunk]:
    raw_words = query.lower().split()
    query_words = []
    for word in raw_words:
        cleaned_word = word.strip(string.punctuation)
        if cleaned_word and cleaned_word not in STOP_WORDS:
            query_words.append(cleaned_word)

    scored_chunks = []
    for chunk in chunks:
        chunk_text_lower = chunk.text.lower()
        chunk_words_raw = chunk_text_lower.split()
        chunk_words = [w.strip(string.punctuation) for w in chunk_words_raw]

        score = 0
        for word in query_words:
            if word in chunk_words:
                score += 1
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda pair: pair[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:top_k]]