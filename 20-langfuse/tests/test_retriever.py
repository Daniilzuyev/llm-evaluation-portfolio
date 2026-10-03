import pytest
from app.retriever import tokenize, singular

@pytest.mark.parametrize(
    "word, expected",
    [
        ("fees", "fee"),
        ("class", "class"),
        ("bus", "bus"),
    ],
)
def test_singular(word, expected):
    assert singular(word) == expected

def test_tokenize_drops_stop_words_and_singularizes():
    assert tokenize("What is the fee for my cards?") == {"fee", "card"}

def test_tokenize_excludes_stop_words():
    result = tokenize("the fee for my card")
    assert "the" not in result
    assert "my" not in result