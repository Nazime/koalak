from koalak.containers import Container, DictContainer

from .utils import Person


def test_distinct():
    people = Container(
        [
            Person("Alice", 30, ["friendly", "smart"]),
            Person("Bob", 25, ["kind", "smart"]),
            Person("Charlie", 30, ["friendly"]),
        ]
    )

    assert people.distinct("name") == ["Alice", "Bob", "Charlie"]
    assert people.distinct("age") == [30, 25]
