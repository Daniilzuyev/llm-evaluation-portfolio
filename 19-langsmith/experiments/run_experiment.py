from dotenv import load_dotenv
load_dotenv()

from langsmith import Client

from app.pipeline import answer_pipeline
from datasets.upload_dataset import DATASET_NAME
from experiments.evaluators import matches_expected, no_phone_number


def target(inputs: dict) -> dict:
    return {"answer": answer_pipeline(inputs["query"])}

if __name__ == "__main__":
    client = Client()
    client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[no_phone_number, matches_expected],
        experiment_prefix="tokenize-singular",
    )