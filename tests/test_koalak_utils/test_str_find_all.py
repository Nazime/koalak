from koalak.utils import str_find_all


def test_str_find_all():
    # Test normal behavior
    assert str_find_all("hello world", "l") == [2, 3, 9]
    assert str_find_all("hello world", "lo") == [3]
    assert str_find_all("hello world", "x") == []

    # Test overlap behavior
    assert str_find_all("ababa", "aba", overlap=True) == [0, 2]

    # Test return_position behavior
    assert str_find_all("hello world", "l", return_position=True) == [
        (2, 3),
        (3, 4),
        (9, 10),
    ]
    assert str_find_all("hello world", "lo", return_position=True) == [(3, 5)]
    assert str_find_all("hello world", "x", return_position=True) == []


def test_str_find_all_with_start_and_end():
    assert str_find_all("hello world", "l", start=3) == [3, 9]
    assert str_find_all("hello world", "l", start=4) == [9]
    assert str_find_all("hello world", "l", start=10) == []
    assert str_find_all("hello world", "l", end=3) == [2]
    assert str_find_all("hello world", "l", end=4) == [2, 3]
    assert str_find_all("hello world", "l", end=2) == []
    assert str_find_all("hello world", "l", start=3, end=6) == [3]
    assert str_find_all("hello world", "l", start=3, end=3) == []
