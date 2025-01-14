from koalak.utils import dict_update_without_overwrite


# Writing tests for the function
def test_basic_update():
    d1 = {"a": 1, "b": 2}
    d2 = {"c": 3}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"a": 1, "b": 2, "c": 3}


def test_no_overwrite():
    d1 = {"a": 1}
    d2 = {"a": 2}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"a": 1}


def test_recursive_update():
    d1 = {"nested": {"a": 1}}
    d2 = {"nested": {"b": 2}}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"nested": {"a": 1, "b": 2}}


def test_recursive_no_overwrite():
    d1 = {"nested": {"a": 1}}
    d2 = {"nested": {"a": 2}}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"nested": {"a": 1}}


def test_empty_dict_update():
    d1 = {}
    d2 = {"a": 1}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"a": 1}


def test_update_with_empty_dict():
    d1 = {"a": 1}
    d2 = {}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"a": 1}


def test_update_with_multiple_levels():
    d1 = {"level1": {"level2": {"a": 1}}}
    d2 = {"level1": {"level2": {"b": 2}, "new_level2": {"c": 3}}}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"level1": {"level2": {"a": 1, "b": 2}, "new_level2": {"c": 3}}}


def test_update_with_nested_dicts():
    d1 = {"outer": {"inner": {"key1": "value1"}}}
    d2 = {"outer": {"inner": {"key2": "value2"}, "new_inner": {"key3": "value3"}}}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {
        "outer": {
            "inner": {"key1": "value1", "key2": "value2"},
            "new_inner": {"key3": "value3"},
        }
    }


def test_update_with_deeply_nested_structure():
    d1 = {"a": {"b": {"c": {"d": 1}}}}
    d2 = {"a": {"b": {"c": {"e": 2}, "f": 3}, "g": 4}}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"a": {"b": {"c": {"d": 1, "e": 2}, "f": 3}, "g": 4}}


def test_update_with_mixed_types():
    d1 = {"a": 1, "b": {"c": 2}}
    d2 = {"a": {"new": 3}, "b": 3}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"a": 1, "b": {"c": 2}}


def test_overwrite_with_non_dict():
    d1 = {"a": {"b": 1}}
    d2 = {"a": 2}
    dict_update_without_overwrite(d1, d2)
    assert d1 == {"a": {"b": 1}}
