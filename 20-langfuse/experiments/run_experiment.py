from dotenv import load_dotenv
load_dotenv()

import sys

from langfuse import get_client

from app.pipeline import answer_pipeline
from experiments.evaluators import matches_expected, no_phone_number

DATASET_NAME = "imagine-bank-support-qa"


def task(*, item, **kwargs):
    return answer_pipeline(item.input["query"])


def main(experiment_name):
    langfuse = get_client()
    dataset = langfuse.get_dataset(DATASET_NAME)
    result = dataset.run_experiment(
        name=experiment_name,
        task=task,
        evaluators=[no_phone_number, matches_expected],
        max_concurrency=1,
    )
    langfuse.flush()
    print(result.format(include_item_results=True))


if __name__ == "__main__":
    main(sys.argv[1])