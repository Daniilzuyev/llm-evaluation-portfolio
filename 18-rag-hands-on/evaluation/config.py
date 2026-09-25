from ragas.llms import llm_factory
from pathlib import Path
from langchain_openai import OpenAIEmbeddings as LCEmbeddings
from ragas.embeddings import OpenAIEmbeddings
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from dotenv import load_dotenv
from data.test_cases import TEST_CASES
from langchain_chroma import Chroma
from rag_system.chain import run_pipeline
from pydantic import BaseModel

class QACase(BaseModel):
    case_id: str
    user_input: str
    retrieved_contexts: list[str]
    response: str
    reference: str

load_dotenv()

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
HR_DOCS_DIR = PROJECT_ROOT / "data" / "hr_docs"
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")

anthropic_client = AsyncAnthropic()
openai_client = AsyncOpenAI()

judge_llm = llm_factory(
    model="claude-sonnet-5",
    provider="anthropic",
    client=anthropic_client,
)
judge_llm.model_args.pop("temperature", None)
judge_llm.model_args.pop("top_p", None)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    client=openai_client
)

vectorstore = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=LCEmbeddings()
)

def get_ragas_cases():
    result = []
    for tc in TEST_CASES:
        if tc.reference is not None:
            result.append(tc)
    return result

def build_qa_cases() -> list[QACase]:
    ragas_test_cases = get_ragas_cases()

    qa_cases = []
    for tc in ragas_test_cases:
        result = run_pipeline(vectorstore, tc.query)
        qa_cases.append(QACase(
            case_id=tc.id,
            user_input=tc.query,
            retrieved_contexts=result.retrieved_contexts,
            response=result.answer,
            reference=tc.reference
        ))
    return qa_cases

if __name__ == "__main__":
    cases = build_qa_cases()
    print(len(cases))
    print(cases[0])