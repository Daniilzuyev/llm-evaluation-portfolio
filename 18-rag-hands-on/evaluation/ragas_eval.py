from data.test_cases import TEST_CASES
from typing import Optional
from pydantic import BaseModel
from ragas.dataset import Dataset
from ragas.backends.inmemory import InMemoryBackend
from ragas.metrics.collections import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from ragas import experiment
import asyncio
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings as LCEmbeddings
from pathlib import Path
from dotenv import load_dotenv
from evaluation.config import judge_llm, embeddings
from rag_system.chain import run_pipeline

load_dotenv()

CURRENT_FILE = Path(__file__)
PROJECT_ROOT = CURRENT_FILE.parent.parent
CHROMA_DIR = str(PROJECT_ROOT / "chroma_db")

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

class QACase(BaseModel):
    case_id: str
    user_input: str
    retrieved_contexts: list[str]
    response: str
    reference: str


class ExperimentResult(BaseModel):
    case_id: str
    faithfulness: float
    faithfulness_reason: Optional[str] = None
    answer_relevancy: float
    answer_relevancy_reason: Optional[str] = None
    context_precision: float
    context_precision_reason: Optional[str] = None
    context_recall: float
    context_recall_reason: Optional[str] = None

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

faithfulness_metric = Faithfulness(llm=judge_llm)
answer_relevancy_metric = AnswerRelevancy(llm=judge_llm, embeddings=embeddings)
context_precision_metric = ContextPrecision(llm=judge_llm)
context_recall_metric = ContextRecall(llm=judge_llm)

@experiment(ExperimentResult)
async def run_evaluate(row: QACase) -> ExperimentResult:
    faith = await faithfulness_metric.ascore(
        user_input=row.user_input,
        response=row.response,
        retrieved_contexts=row.retrieved_contexts,
    )

    relevancy = await answer_relevancy_metric.ascore(
        user_input=row.user_input,
        response=row.response
    )

    precision = await context_precision_metric.ascore(
        user_input=row.user_input,
        retrieved_contexts=row.retrieved_contexts,
        reference=row.reference,
    )
    recall = await context_recall_metric.ascore(
        user_input=row.user_input,
        retrieved_contexts=row.retrieved_contexts,
        reference=row.reference,
    )
    return ExperimentResult(
        case_id=row.case_id,
        faithfulness=faith.value, faithfulness_reason=faith.reason,
        answer_relevancy=relevancy.value, answer_relevancy_reason=relevancy.reason,
        context_precision=precision.value, context_precision_reason=precision.reason,
        context_recall=recall.value, context_recall_reason=recall.reason
    )

dataset = Dataset(
    name="rag_eval_dataset",
    backend=InMemoryBackend(),
    data_model=QACase,
    data=build_qa_cases()
)

async def main() -> None:
    results = await run_evaluate.arun(dataset)
    for row in results:
        print(row)
    return results


if __name__ == "__main__":
    asyncio.run(main())