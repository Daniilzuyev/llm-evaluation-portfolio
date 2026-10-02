import re

from langsmith import traceable

from app.corpus import load_chunks

STOP_WORDS = {
    "what", "is", "the", "for", "a", "my", "of", "to", "do", "i", "in"
}


def singular(word: str) -> str:
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def tokenize(text: str) -> set[str]:
    tokens = set()
    words = re.findall(r"[a-z0-9]+", text.lower())
    for word in words:
        if word in STOP_WORDS:
            continue
        tokens.add(singular(word))
    return tokens


def score_chunks(query, chunks):
    query_words = tokenize(text=query)
    scored = []
    for chunk in chunks:
        chunk_words = tokenize(text=chunk.text)
        score = len(query_words & chunk_words)
        scored.append((score, chunk))
    return scored


@traceable
def retrieve(query, chunks, k=3):
    scored = score_chunks(query, chunks)
    scored.sort(key=lambda pair: pair[0], reverse=True)
    relevant = [(score, chunk) for score, chunk in scored if score > 0]
    top = relevant[:k]
    return [chunk for score, chunk in top]


if __name__ == "__main__":
    chunks = load_chunks()
    for query in ["I losed my card, which should be my next steps?",
                  "What is my transfer limit?"]:
        print(query)
        for chunk in retrieve(query, chunks):
            print("  ", chunk.text[:40])