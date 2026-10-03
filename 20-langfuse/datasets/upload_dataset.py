from dotenv import load_dotenv

load_dotenv()

from langfuse import get_client

from data.eval_cases import TEST_CASES

DATASET_NAME = "imagine-bank-support-qa"


def main():
    langfuse = get_client()

    langfuse.create_dataset(
        name=DATASET_NAME,
        description="Imagine Bank support bot: 12 cases, failure_mode in metadata",
    )

    for number, case in enumerate(TEST_CASES, start=1):
        langfuse.create_dataset_item(
            dataset_name=DATASET_NAME,
            id=f"{DATASET_NAME}-{number:02d}",
            input={"query": case["query"]},
            expected_output={"expected": case["expected"]},
            metadata={"failure_mode": case["failure_mode"]},
        )

    langfuse.flush()
    print(f"Uploaded {len(TEST_CASES)} items to {DATASET_NAME}")


if __name__ == "__main__":
    main()