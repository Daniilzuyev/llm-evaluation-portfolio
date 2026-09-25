from dataclasses import dataclass
import frontmatter
from datetime import date
from pathlib import Path
from langchain_core.documents import Document as LCDocument
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
HR_DOCS_DIR = PROJECT_ROOT / "data" / "hr_docs"
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")


@dataclass
class Document:
    id: str
    title: str
    content: str
    last_updated: date

def load_corpus() -> list[Document]:
    documents = []
    for path in HR_DOCS_DIR.glob("*.md"):
        post = frontmatter.load(path)
        doc = Document(
            id=post.metadata["id"],
            title=post.metadata["title"],
            content=post.content,
            last_updated=post.metadata["last_updated"]
        )
        documents.append(doc)
    return documents


@dataclass
class Chunk:
    text: str
    doc_id: str
    doc_last_updated: date


def chunk_document(doc: Document) -> list[Chunk]:
    paragraphs = doc.content.split("\n\n")
    chunks = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        chunk = Chunk(
            text=para,
            doc_id=doc.id,
            doc_last_updated=doc.last_updated
        )
        chunks.append(chunk)
    return chunks


def chunk_corpus(documents: list[Document]) -> list[Chunk]:
    chunks = []
    for doc in documents:
        doc_chunks = chunk_document(doc)
        chunks.extend(doc_chunks)
    return chunks

def chunks_to_documents(chunks: list[Chunk]) -> list[LCDocument]:
    docs = []
    for chunk in chunks:
        doc = LCDocument(
            page_content=chunk.text,
            metadata={
                "doc_id": chunk.doc_id,
                "doc_last_updated": str(chunk.doc_last_updated)
            }
        )
        docs.append(doc)
    return docs

def build_vectorstore(documents: list[LCDocument], persist_dir: str) -> Chroma:
    model = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=model,
        persist_directory=persist_dir
    )
    return vectorstore


if __name__ == "__main__":
     docs = load_corpus()
     chunks = chunk_corpus(docs)
     lc_docs = chunks_to_documents(chunks)
     vectorstore = build_vectorstore(lc_docs, CHROMA_DIR)
     print(f"Vectorstore built: {len(lc_docs)} documents indexed")