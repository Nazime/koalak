import os

from koalak.utils import (
    get_prefixed_callables_of_object,
    merge_intervals,
    randomstr,
    str_find_all,
    temp_pathname,
)


def test_randomstr():
    # By default the function work (no need the first param)
    randomstr()

    # test length
    for _ in range(20):
        assert len(randomstr(10)) == 10
        assert len(randomstr(20)) == 20

    # test alphabet
    alphabet = "abc"
    for _ in range(20):
        a = randomstr(alphabet=alphabet)
        for c in a:
            assert c in alphabet

    # test exclude
    alphabet = "ab"
    a = randomstr(1, alphabet=alphabet, exclude="a")
    assert a == "b"

    # test prefix
    for _ in range(20):
        assert randomstr(prefix="ab_").startswith("ab_")


def test_temp_pathname():
    # Test that if we create a file, it is correctly removed
    with temp_pathname() as pathname:
        saved_pathname = pathname
        assert not os.path.exists(pathname)
        # create the file
        open(pathname, "w")

        assert os.path.exists(pathname)
    assert not os.path.exists(saved_pathname)

    # Test that if we create a directory, it is correctly removed
    with temp_pathname() as pathname:
        saved_pathname = pathname
        assert not os.path.exists(pathname)
        # create the file
        os.makedirs(os.path.join(pathname, "test"))
        assert os.path.exists(pathname)
    assert not os.path.exists(saved_pathname)

    # Test that the file is correctly removed after an exception
    class DummyException(Exception):
        pass

    try:
        with temp_pathname() as pathname:
            # create the file
            open(pathname, "w")
            raise DummyException
    except DummyException:
        assert not os.path.exists(pathname)


def test_get_prefixed_callables_of_object():
    class A:
        test_nop = "something"

        def f(self):
            pass

        def test_a(self):
            pass

        def test_b(self):
            pass

    a = A()
    assert get_prefixed_callables_of_object(a, "test_") == [a.test_a, a.test_b]

    class B:
        test_nop = "something"
        run_z = "something"

        def f(self):
            pass

        def test_a(self):
            pass

        def test_b(self):
            pass

        def run_x(self):
            pass

        def run_y(self):
            pass

    b = B()
    assert get_prefixed_callables_of_object(b, "test_") == [b.test_a, b.test_b]
    assert get_prefixed_callables_of_object(b, "run_") == [b.run_x, b.run_y]


def test_merge_intervals():
    # Test merging of non-overlapping intervals
    intervals = [(1, 3), (5, 8), (10, 12)]
    assert merge_intervals(intervals) == intervals

    # Test merging of partially overlapping intervals
    intervals = [(1, 3), (2, 6), (5, 8)]
    assert merge_intervals(intervals) == [(1, 8)]

    # Test merging of fully overlapping intervals
    intervals = [(1, 3), (2, 6), (3, 4)]
    assert merge_intervals(intervals) == [(1, 6)]

    # Test merging of mixed intervals
    intervals = [(1, 3), (2, 6), (8, 10), (15, 18)]
    assert merge_intervals(intervals) == [(1, 6), (8, 10), (15, 18)]

    # Test merging of empty list
    intervals = []
    assert merge_intervals(intervals) == intervals


# Merge all the tests for find_all_indexes into one function
def test_find_all_indexes():
    # Test 1: Basic functionality with no overlap
    string = "hello world"
    substring = "l"
    expected = [2, 3, 9]
    assert str_find_all(string, substring) == expected

    # Test 3: Substring not found
    string = "hello world"
    substring = "z"
    expected = []
    assert str_find_all(string, substring) == expected

    # Test 4: Empty string
    string = ""
    substring = "z"
    expected = []
    assert str_find_all(string, substring) == expected

    # Test 8: No overlap with multi-character substring
    string = "hello world"
    substring = "lo"
    expected = [3]
    assert str_find_all(string, substring) == expected

    # TODO: add testing when overlaping, and for long charaters
