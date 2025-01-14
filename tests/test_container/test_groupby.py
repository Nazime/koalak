import pytest
from koalak.containers import Container, DictContainer

from .utils import Person


def test_container_groupby():
    container = Container(
        [
            Person("Alice", 30, ["friendly", "smart"]),
            Person("Bob", 25, ["kind", "smart"]),
            Person("Charlie", 35, ["friendly"]),
            Person("John", 25, ["smart"]),
        ]
    )

    # Grouping by a specified attribute
    grouped_data = dict(container.groupby("age"))

    # Check the number of groups
    assert len(grouped_data) == 3

    # Test for the first age group
    group = grouped_data[30]
    assert len(group) == 1
    member = group[0]
    assert member.name == "Alice"
    assert member.age == 30

    # Test for the second age group
    group = grouped_data[25]
    assert len(group) == 2
    member = group[0]
    assert member.name == "Bob"
    assert member.age == 25
    member = group[1]
    assert member.name == "John"
    assert member.age == 25

    # Test for the third age group
    group = grouped_data[35]
    assert len(group) == 1
    member = group[0]
    assert member.name == "Charlie"
    assert member.age == 35


def test_dict_container_groupby():
    container = DictContainer(
        [
            {"name": "Alice", "age": 30, "traits": ["friendly", "smart"]},
            {"name": "Bob", "age": 25, "traits": ["kind", "smart"]},
            {"name": "Charlie", "age": 35, "traits": ["friendly"]},
            {"name": "John", "age": 25, "traits": ["smart"]},
        ]
    )

    # Grouping by a specified attribute
    grouped_data = dict(container.groupby("age"))

    # Check the number of groups
    assert len(grouped_data) == 3

    # Test for the first age group
    group = grouped_data[30]
    assert len(group) == 1
    member = group[0]
    assert member["name"] == "Alice"
    assert member["age"] == 30

    # Test for the second age group
    group = grouped_data[25]
    assert len(group) == 2
    member = group[0]
    assert member["name"] == "Bob"
    assert member["age"] == 25
    member = group[1]
    assert member["name"] == "John"
    assert member["age"] == 25

    # Test for the third age group
    group = grouped_data[35]
    assert len(group) == 1
    member = group[0]
    assert member["name"] == "Charlie"
    assert member["age"] == 35
