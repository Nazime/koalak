from koalak.containers import search

from .utils import Person


def test_magic_search_simple_str():
    people = [Person("alice", 30), Person("bob", 25), Person("charlie", 35)]
    results = list(search(people, name="alice"))
    assert len(results) == 1
    e = results[0]
    assert e is people[0]
    assert e.name == "alice"
    assert e.age == 30


def test_search_simple_int():
    people = [Person("alice", 30), Person("bob", 25), Person("charlie", 35)]
    results = list(search(people, age=25))
    assert len(results) == 1
    e = results[0]
    assert e is people[1]
    assert e.name == "bob"
    assert e.age == 25


def test_search_simple_no_int():
    data = [Person("alice", 30), Person("bob", 25), Person("charlie", 35)]

    results = list(search(data, age__not=25))
    assert len(results) == 2
    assert all(person.age != 25 for person in results)


def test_search_simple_list_of_str():
    data = [
        Person("alice", 30, tags=["charlie", "david"]),
        Person("bob", 25, tags=["eva"]),
        Person("charlie", 35, tags=["alice"]),
    ]

    results = list(search(data, tags="charlie"))
    assert len(results) == 1
    assert results[0].name == "alice"
    assert "charlie" in results[0].tags


def test_search_no_as_list():
    data = [
        Person("alice", 30, tags=["charlie", "david"]),
        Person("bob", 25, tags=["eva"]),
        Person("charlie", 35, tags=["alice"]),
    ]

    results = list(search(data, name__not=["alice", "charlie"]))
    assert len(results) == 1
    assert results[0].name == "bob"
