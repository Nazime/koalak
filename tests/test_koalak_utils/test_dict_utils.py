from koalak.utils import dict_flat, json_nested_items, json_nested_loads


def test_dict_flat_simple():
    input_dict = {"a": 1, "b": 2}
    expected = {"a": 1, "b": 2}
    assert dict_flat(input_dict) == expected


def test_dict_flat_nested():
    input_dict = {"a": {"b": 1, "c": 2}}
    expected = {"a.b": 1, "a.c": 2}
    assert dict_flat(input_dict) == expected


def test_dict_flat_deeply_nested():
    input_dict = {"a": {"b": {"c": 1}}}
    expected = {"a.b.c": 1}
    assert dict_flat(input_dict) == expected


def test_dict_flat_empty_dict():
    assert dict_flat({}) == {}


def test_dict_flat_mixed_types():
    input_dict = {"a": 1, "b": {"c": 2, "d": [3, 4]}}
    expected = {"a": 1, "b.c": 2, "b.d": [3, 4]}
    assert dict_flat(input_dict) == expected


def test_json_nested_loads_with_string():
    input_str = '{"key": "{\\"nestedKey\\": \\"nestedValue\\"}"}'
    expected = {"key": {"nestedKey": "nestedValue"}}
    assert json_nested_loads(input_str) == expected


def test_json_nested_loads_with_dict():
    input_dict = {"key": '{"nestedKey": "nestedValue"}'}
    expected = {"key": {"nestedKey": "nestedValue"}}
    assert json_nested_loads(input_dict) == expected


def test_json_nested_loads_with_non_json_string():
    non_json_str = "just a string"
    assert json_nested_loads(non_json_str) == non_json_str


def test_json_nested_loads_with_nested_json_string():
    input_dict = {"key": '{"nestedKey": "nestedValue"}'}
    expected = {"key": {"nestedKey": "nestedValue"}}
    assert json_nested_loads(input_dict) == expected


def test_json_nested_loads_with_mixed_types():
    input_dict = {
        "int": 1,
        "string": "value",
        "dict_string": '{"nestedKey": "nestedValue"}',
    }
    expected = {
        "int": 1,
        "string": "value",
        "dict_string": {"nestedKey": "nestedValue"},
    }
    assert json_nested_loads(input_dict) == expected


def test_json_nested_loads_dict_with_nested_dicts():
    input_dict = {"level1": {"level2": '{"nestedKey": "nestedValue"}'}}
    expected = {"level1": {"level2": {"nestedKey": "nestedValue"}}}
    assert json_nested_loads(input_dict) == expected


def test_json_nested_loads_string_with_invalid_json():
    invalid_json_str = '{"key": "value}'
    assert json_nested_loads(invalid_json_str) == invalid_json_str


def test_json_nested_loads_empty_string():
    assert json_nested_loads("") == ""


def test_json_nested_items_with_dict():
    input_obj = {"a": {"b": 1}, "c": 2}
    expected = {"a.b": 1, "c": 2}
    assert dict(json_nested_items(input_obj)) == expected


def test_json_nested_items_with_list():
    input_obj = [{"a": 1}, {"b": 2}, {"c": {"d": 3}}]
    expected = {"[].a": 1, "[].b": 2, "[].c.d": 3}
    assert dict(json_nested_items(input_obj)) == expected


def test_json_nested_items_with_mixed_types():
    input_obj = {"a": [{"b": 1}, {"c": 2}], "d": {"e": 3}}
    expected = {"a.[].b": 1, "a.[].c": 2, "d.e": 3}
    assert dict(json_nested_items(input_obj)) == expected
