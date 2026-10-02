from dotenv import load_dotenv
load_dotenv()

from langsmith import Client

from data.eval_cases import TEST_CASES

DATASET_NAME = "imagine-bank-support-qa"


def upload_dataset() -> None:
    client = Client()

    if client.has_dataset(dataset_name=DATASET_NAME):
        print(f"Dataset '{DATASET_NAME}' already exists, skipping.")
        return

    client.create_dataset(
        DATASET_NAME,
        description="Imagine Bank support bot: baseline, ambiguity, out-of-scope, no-data-request cases.",
    )

    examples = [
        {
            "inputs": {"query": case["query"]},
            "outputs": {"expected": case["expected"]},
            "metadata": {"failure_mode": case["failure_mode"]},
        }
        for case in TEST_CASES
    ]

    client.create_examples(dataset_name=DATASET_NAME, examples=examples)
    print(f"Uploaded {len(examples)} examples to '{DATASET_NAME}'.")


if __name__ == "__main__":
    upload_dataset()