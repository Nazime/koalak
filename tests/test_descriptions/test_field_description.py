from typing import List, Set

import attrs
import pytest
from koalak.descriptions.field_description import FieldDescription


def test_default_values():
    field = FieldDescription()

    assert field.name is None

    # attributes related to arguments/parameters
    assert field.kw_only is False
    assert field.default is attrs.NOTHING
    assert field.required is True
    assert field.annotation is None

    # attributes related to type checking
    assert field.type is None
    assert field.choices is None  # FIXME: None or list?

    # attributes related to documentation
    assert field.description is None
    assert field.examples is None

    # attributes related to database
    assert field.unique is False
    assert field.indexed is False


def test_generic_field_if_default_required_is_false():
    field = FieldDescription(default=10)
    assert field.default == 10
    assert field.required is False


def test_generic_field_error_when_default_and_factory_are_set():
    with pytest.raises(ValueError):
        FieldDescription(default=10, factory=list)


def test_method_get_default():
    field = FieldDescription()
    assert field.get_default() is attrs.NOTHING

    field = FieldDescription(default=10)
    assert field.default == 10

    field = FieldDescription(factory=list)
    l1 = field.get_default()
    assert l1 == []

    l2 = field.get_default()
    assert l2 == []

    assert l1 is not l2


def test_required_property():
    field = FieldDescription()
    assert field.required is True

    field = FieldDescription(default=10)
    assert field.required is False

    field = FieldDescription(factory=list)
    assert field.required is False


def test_equality():
    assert FieldDescription() == FieldDescription()
    assert FieldDescription("name") == FieldDescription("name")

    assert FieldDescription(kw_only=True) != FieldDescription(kw_only=False)
    assert FieldDescription("a") != FieldDescription("b")


def test_atomic_type_and_origin_annotation():
    field = FieldDescription(annotation=str)
    assert not field.is_list()
    assert not field.is_set()
    assert field.is_atomic()
    assert field.atomic_type is str

    field = FieldDescription(annotation=List[str])
    assert field.is_list()
    assert not field.is_set()
    assert not field.is_atomic()
    assert field.atomic_type is str

    field = FieldDescription(annotation=Set[int])
    assert not field.is_list()
    assert field.is_set()
    assert not field.is_atomic()
    assert field.atomic_type is int

    # try with typing.Set
    field = FieldDescription(annotation=Set["Custom"])
    assert not field.is_list()
    assert field.is_set()
    assert not field.is_atomic()
    assert field.atomic_type == "Custom"

    # try with built in set
    field = FieldDescription(annotation=set["Custom"])
    assert not field.is_list()
    assert field.is_set()
    assert not field.is_atomic()
    assert field.atomic_type == "Custom"


def test_field_description_from_dict():
    # Case 1: Simple field without `type_as_str`
    field_data1 = {"name": "age", "type": int}
    field1 = FieldDescription.from_dict(field_data1)
    assert field1.name == "age"
    assert field1.type is int

    # Case 2: Field with `type_as_str` set to True and a type string
    field_data2 = {"name": "price", "type": "int"}
    field2 = FieldDescription.from_dict(field_data2, type_as_str=True)
    assert field2.name == "price"
    assert field2.type is int

    # Case 3: Field with a type not in `_map_str_to_type` (should keep the original type string)
    field_data3 = {"name": "status", "type": "Custom"}
    field3 = FieldDescription.from_dict(field_data3, type_as_str=True)
    assert field3.name == "status"
    assert field3.type == "Custom"

    # Case 4: Field with a missing `type` (should use default values)
    field_data4 = {"name": "description"}
    field4 = FieldDescription.from_dict(field_data4)
    assert field4.name == "description"
    assert field4.type is None


def test_nullable():
    assert FieldDescription().nullable is False
    assert FieldDescription(nullable=True).nullable is True
    # If default is None then field can be nullable
    assert FieldDescription(default=None).nullable is True
    assert FieldDescription(default=10).nullable is False
    with pytest.raises(ValueError):
        FieldDescription(default=None, nullable=False)


def test_hide_fields():
    # By default all hide are False
    field = FieldDescription()
    assert not field.hidden
    assert field.shown
    assert not field.hidden_in_list
    assert field.show_in_list
    assert not field.hidden_in_detail
    assert field.show_in_detail

    # Setting hide will hide all other hide fields
    field = FieldDescription(hidden=True)
    assert field.hidden
    assert not field.shown
    assert field.hidden_in_list
    assert not field.show_in_list
    assert field.hidden_in_detail
    assert not field.show_in_detail

    # hide can not work if hide_in_list and hide_in_detail are different
    field = FieldDescription(hidden_in_list=True)
    with pytest.raises(ValueError):
        field.hidden
    with pytest.raises(ValueError):
        field.shown
    assert field.hidden_in_list
    assert not field.show_in_list
    assert not field.hidden_in_detail
    assert field.show_in_detail

    field = FieldDescription(hidden_in_detail=True)
    with pytest.raises(ValueError):
        field.hidden
    with pytest.raises(ValueError):
        field.shown
    assert not field.hidden_in_list
    assert field.show_in_list
    assert field.hidden_in_detail
    assert not field.show_in_detail

    # Check when it's False
    field = FieldDescription(hidden_in_detail=False)
    assert not field.hidden
    assert field.shown
    assert not field.hidden_in_list
    assert field.show_in_list
    assert not field.hidden_in_detail
    assert field.show_in_detail


@pytest.mark.skip
def test_converters():
    field = FieldDescription(converters=[int])
    assert field.init("12") == 12
