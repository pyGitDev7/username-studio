import pytest

from username_filter import UsernameFilter, create_filter


@pytest.mark.parametrize(
    "username",
    [
        "noria",
        "@NORIA",
        "Lumen",
        "cafe",
    ],
)
def test_accepts_normalized_valid_usernames(username):
    username_filter = UsernameFilter(min_length=4, max_length=6)

    assert username_filter.is_valid(username)


@pytest.mark.parametrize(
    "username",
    [
        "",
        "nor",
        "lumenae",
        "nor1a",
        "nor_a",
        "about",
        "aaaao",
        "qzxao",
        "bcdfg",
    ],
)
def test_rejects_bad_usernames(username):
    username_filter = UsernameFilter(min_length=4, max_length=6)

    assert not username_filter.is_valid(username)


def test_filter_batch_normalizes_and_removes_invalid_items():
    username_filter = UsernameFilter(min_length=5, max_length=6)

    result = username_filter.filter_batch([" @Noria! ", "LuméN", "nor1a", "bcdfg"])

    assert result == ["noria", "lumen"]


def test_excluded_usernames_are_rejected_case_insensitively():
    username_filter = create_filter({"noria"}, min_length=5, max_length=6)

    assert not username_filter.is_valid("NORIA")
    assert username_filter.is_valid("lumen")


def test_remove_duplicates_normalizes_input_order():
    username_filter = UsernameFilter(min_length=5, max_length=6)

    assert username_filter.remove_duplicates(["Noria", "@noria", "LuméN", "!!!"]) == ["noria", "lumen"]


def test_allow_digits_requires_letter_first():
    username_filter = UsernameFilter(min_length=5, max_length=6, allow_digits=True)

    assert username_filter.is_valid("a1e2o")
    assert not username_filter.is_valid("1aeon")
