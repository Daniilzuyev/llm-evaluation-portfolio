from dataclasses import dataclass
import frontmatter
from pathlib import Path

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
HR_DOCS_DIR = PROJECT_ROOT / "data" / "hr_docs"

@dataclass
class Document:
    id: str
    title: str
    content: str
    last_updated: str

def load_corpus() -> list[Document]:
    documents = []
    for path in HR_DOCS_DIR.glob("*.md"):
        post = frontmatter.load(path)
        doc = Document(
            id = post.metadata["id"],
            title = post.metadata["title"],
            content=post.content,
            last_updated=post.metadata["last_updated"]
        )
        documents.append(doc)
    return documents
