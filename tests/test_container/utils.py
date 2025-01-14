from typing import List

import pytest


class Person:
    def __init__(
        self, name: str, age: int = None, money: float = None, *, tags: List[str] = None
    ):
        self.name = name
        self.age = age
        self.tags = tags
        self.money = money

    def __str__(self):
        return (
            f"Person({self.name}, age={self.age}, money={self.money}, tags={self.tags})"
        )

    def __repr__(self):
        return self.__str__()


@pytest.fixture
def people_dict_data():
    return [
        {"name": "Alice", "age": 30, "money": 50, "tags": ["friendly", "smart"]},
        {"name": "Bob", "age": 25, "money": 50, "tags": ["kind", "smart"]},
        {"name": "Charlie", "age": 35, "money": 500, "tags": ["friendly"]},
    ]


@pytest.fixture
def people_data(people_dict_data):
    return [Person(**person_dict) for person_dict in people_dict_data]
