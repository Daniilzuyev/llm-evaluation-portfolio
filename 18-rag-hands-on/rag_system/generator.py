from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document as LCDocument

load_dotenv()

def build_context(documents: list[LCDocument]) -> str:
    result = []
    for doc in documents:
        result.append(doc.page_content)
    return "\n\n".join(result)

def generate_answer(query: str,context: str) -> str:
    llm = ChatAnthropic(model="claude-haiku-4-5")
    messages = [
        {"role": "system", "content": "You are HR assistant. Answer the question using ONLY the information in provided context. If the context does not contain enough information to answer, say so explicit. Do not state any fact that is not present in the context."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]
    response = llm.invoke(messages)
    return response.content

if __name__ == "__main__":
    test_docs = [
        LCDocument(page_content="Employees in the US office get 15 vacation days per year."),
        LCDocument(page_content="Vacation requests must be submitted 2 weeks in advance.")
    ]
    context = build_context(test_docs)
    answer = generate_answer("How many vacation days in the US?", context)
    print(answer)