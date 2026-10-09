from dataclasses import dataclass
import frontmatter
from pathlib import Path

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
BANK_DOCS_DIR = PROJECT_ROOT / "data" / "bank_docs"

@dataclass
class Chunk:
    doc_title: str
    text: str
    last_updated: str

def load_chunks() -> list[Chunk]:
    chunks = []
    for path in sorted(BANK_DOCS_DIR.glob("*.md")):
        post = frontmatter.load(path)
        for paragraph in post.content.split("\n\n"):
            paragraph = paragraph.strip()
            if not paragraph or paragraph.startswith("#"):
                continue
            chunk = Chunk(
                doc_title=post.metadata["title"],
                text=paragraph,
                last_updated=str(post.metadata["last_updated"]),
            )
            chunks.append(chunk)
    return chunks


if __name__ == "__main__":
    chunks = load_chunks()
    print(len(chunks))
    print(chunks[2])
