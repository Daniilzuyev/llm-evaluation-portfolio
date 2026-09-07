from data.sample_qa_dataset import qa_dataset
from evaluation.config import judge_llm, embeddings
from typing import Optional
from evaluation.report import evaluate_thresholds, summarize

from ragas.dataset import Dataset
from ragas.backends.inmemory import InMemoryBackend
from ragas.metrics.collections import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall
from pydantic import BaseModel
from ragas import experiment
import asyncio


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

dataset = Dataset(
    name = 'qa_dataset',
    backend=InMemoryBackend(),
    data_model=QACase,
    data=[QACase(**case) for case in qa_dataset]
)

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
    return ExperimentResult(case_id=row.case_id, faithfulness=faith.value, faithfulness_reason=faith.reason, answer_relevancy=relevancy.value, answer_relevancy_reason=relevancy.reason, context_precision=precision.value, context_precision_reason=precision.reason, context_recall=recall.value, context_recall_reason=recall.reason)

async def main() -> None:
    results = await run_evaluate.arun(dataset)
    threshold_report = evaluate_thresholds(results)
    summary = summarize(threshold_report)
    for row in threshold_report:
        print(row)
    print(summary)


if __name__ == "__main__":
    asyncio.run(main())