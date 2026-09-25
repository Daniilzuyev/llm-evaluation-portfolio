from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document as LCDocument
from dotenv import load_dotenv

load_dotenv()

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")


def retrieve(vectorstore: Chroma, query: str, k: int = 3) -> list[LCDocument]:
    return vectorstore.similarity_search(query, k=k)


if __name__ == "__main__":
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=OpenAIEmbeddings()
    )
    results = retrieve(vectorstore, query="how many vacation days in the US?")
    for doc in results:
        print(doc.page_content)