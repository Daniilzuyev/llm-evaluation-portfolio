import pytest

from app.corpus import Chunk
from app.retriever import retrieve, score_chunks, singular, tokenize
from experiments.evaluators import no_phone_number


@pytest.fixture
def chunks():
    return [
        Chunk("Card Fees", "Imagine Bank Credit Card: the monthly maintenance fee is $8.", "2026-08-15"),
        Chunk("Lost or Stolen Card", "Step 2: Request a replacement in the app.", "2026-06-10"),
        Chunk("Deposit Rates", "Savings account: 2.5% annual interest.", "2025-01-15"),
    ]


@pytest.mark.parametrize("word, expected", [
    ("steps", "step"),
    ("transfers", "transfer"),
    ("cards", "card"),
    ("business", "business"),
    ("us", "us"),
    ("bus", "bus"),
    ("fee", "fee"),
])
def test_singular(word, expected):
    assert singular(word) == expected


def test_tokenize_removes_stop_words_and_punctuation():
    assert tokenize("What is the monthly fee for a credit card?") == {
        "monthly", "fee", "credit", "card"
    }


def test_tokenize_keeps_digits_and_drops_symbols():
    assert tokenize("Imagine Bank Credit Card: the monthly maintenance fee is $8.") == {
        "imagine", "bank", "credit", "card", "monthly", "maintenance", "fee", "8"
    }


def test_tokenize_plural_equals_singular():
    assert tokenize("transfers") == tokenize("transfer")


def test_score_chunks_returns_one_pair_per_chunk(chunks):
    scored = score_chunks("monthly fee for a credit card", chunks)
    assert len(scored) == len(chunks)
    assert scored[0][0] == 4
    assert scored[0][1] is chunks[0]


def test_retrieve_best_chunk_first(chunks):
    assert retrieve("monthly fee for a credit card", chunks)[0].doc_title == "Card Fees"


def test_retrieve_empty_when_no_overlap(chunks):
    assert retrieve("weather tomorrow", chunks) == []


def test_retrieve_respects_k(chunks):
    assert len(retrieve("app fee card", chunks, k=1)) == 1
    assert len(retrieve("app fee card", chunks, k=2)) == 2


def test_retrieve_plural_regression():
    # Regression for experiment baseline-haiku: "transfer" in the query
    # did not match "transfers" in the document, retrieve returned [].
    transfers = [Chunk("Transfer Limits", "External transfers to other banks: up to $3,000 per day.", "2026-07-01")]
    assert len(retrieve("What is my transfer limit?", transfers)) == 1


@pytest.mark.parametrize("answer", [
    "Call us at 1-888-790-2887.",
    "Our line is 555.123.4567.",
])
def test_no_phone_number_fails_when_phone_present(answer):
    assert no_phone_number({"answer": answer}) is False


@pytest.mark.parametrize("answer", [
    "A new card arrives within 5-7 business days.",
    "The limit is $3,000 per day and $15,000 per month.",
    "My card number is 4111 1111 1111 1111.",
    "I don't have that information.",
])
def test_no_phone_number_passes_when_no_phone(answer):
    assert no_phone_number({"answer": answer}) is True