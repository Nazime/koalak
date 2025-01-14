import csv
import os

import pytest
from koalak.utils import data_to_csv


def test_data_to_csv_creates_csv_file(tmp_path):
    # Arrange
    file_path = os.path.join(tmp_path, "test.csv")
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

    # Act
    data_to_csv(data, file_path)

    # Assert
    assert os.path.exists(file_path)


def test_data_to_csv_creates_csv_file_with_correct_headers(tmp_path):
    # Arrange
    file_path = os.path.join(tmp_path, "test.csv")
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

    # Act
    data_to_csv(data, file_path)

    # Assert
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
    assert headers == ["name", "age"]


def test_data_to_csv_creates_csv_file_with_correct_data(tmp_path):
    # Arrange
    file_path = os.path.join(tmp_path, "test.csv")
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

    # Act
    data_to_csv(data, file_path)

    # Assert
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    assert rows == [["Alice", "25"], ["Bob", "30"]]


def test_data_to_csv_creates_csv_file_with_custom_delimiter(tmp_path):
    # Arrange
    file_path = os.path.join(tmp_path, "test.csv")
    data = [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}]

    # Act
    data_to_csv(data, file_path, delimiter="|")

    # Assert
    with open(file_path, "r") as f:
        reader = csv.reader(f, delimiter="|")
        headers = next(reader)
        rows = list(reader)
    assert rows == [["Alice", "25"], ["Bob", "30"]]


def test_data_to_csv_creates_csv_file_with_custom_nb_rows_check(tmp_path):
    # Arrange
    file_path = os.path.join(tmp_path, "test.csv")
    data = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30},
        {"name": "Charlie", "age": 35},
    ]

    # Act
    data_to_csv(data, file_path, nb_rows_check=2)

    # Assert
    with open(file_path, "r") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)
    assert headers == ["name", "age"]
    assert rows == [["Alice", "25"], ["Bob", "30"], ["Charlie", "35"]]


def test_data_to_csv_creates_csv_file_with_custom_nb_rows_check_with_non_harmonized_data(
    tmp_path,
):
    # Arrange
    file_path = os.path.join(tmp_path, "test.csv")
    data = [{"name": "Alice"}, {"name": "Bob"}, {"age": 30}]

    # Act
    with pytest.raises(ValueError):
        data_to_csv(data, file_path, nb_rows_check=2)
