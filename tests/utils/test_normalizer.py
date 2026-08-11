import pytest

from material_register.utils.normalizer import normalize_text, normalize_whitespace


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("John", "john"),
        ("JOHN", "john"),
        ("john", "john"),
        ("JoHn", "john"),
        ("  John", "john"),
        ("John  ", "john"),
        ("  John  ", "john"),
        ("   JoHn   ", "john"),
        ("Jérôme O’Connor", "jerome o'connor"),
        ("  JÉRÔME O’CONNOR  ", "jerome o'connor"),
        ("jérôme o’connor", "jerome o'connor"),
        ("  jÉrÔme   O’CoNnOr  ", "jerome o'connor"),
    ],
    ids=[
        "john",
        "john-upper",
        "john-lower",
        "john-mixed",
        "spaces-left",
        "spaces-right",
        "spaces-both",
        "spaces-multi",
        "accent-apostrophe",
        "accent-upper-apostrophe",
        "accent-lower",
        "accent-mixed",
    ],
)
def test_normalize_text_special_chars(input_text, expected):
    assert normalize_text(input_text) == expected


@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("John", "John"),
        ("  John", "John"),
        ("John  ", "John"),
        ("  John  ", "John"),
        ("John   Smith", "John Smith"),
        ("   John   Smith   ", "John Smith"),
        ("A   B   C", "A B C"),
        ("", ""),
        ("   ", ""),
    ],
    ids=[
        "john",
        "leading-spaces",
        "trailing-spaces",
        "both-spaces",
        "double-name",
        "multi-spaces-both",
        "multi-word",
        "empty",
        "only-spaces",
    ],
)
def test_normalize_whitespace(input_text, expected):
    assert normalize_whitespace(input_text) == expected
