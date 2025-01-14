import pytest
from koalak.descriptions import EntityDescription, FieldDescription


def test_generic_field_equality():
    entity = EntityDescription()
    test_field = entity.add_field("test")
    assert test_field == FieldDescription("test")

    assert entity.add_field("attr2", kw_only=True) == FieldDescription(
        "attr2", kw_only=True
    )


def test_dunder_methods():
    entity = EntityDescription()
    assert len(entity) == 0

    filed1 = entity.add_field("firstname")
    assert len(entity) == 1
    assert list(entity) == [filed1]

    field2 = entity.add_field("lastname")
    assert len(entity) == 2
    assert list(entity) == [filed1, field2]


def test_add_existing_field():
    entity = EntityDescription()
    assert len(entity) == 0

    filed1 = entity.add_field("firstname")
    assert len(entity) == 1
    assert list(entity) == [filed1]

    field2 = FieldDescription("lastname")
    entity.add_existing_field(field2)
    assert len(entity) == 2
    assert list(entity) == [filed1, field2]

    with pytest.raises(ValueError):
        # Field without name not allowed
        entity.add_existing_field(FieldDescription())

    with pytest.raises(ValueError):
        # Already existing
        entity.add_existing_field(FieldDescription("firstname"))


def test_builting_attrs_class():
    entity = EntityDescription("persons", cls_name="Person")
    entity.add_field("firstname")
    entity.add_field("lastname")

    Person = entity.build_attrs_dataclass()

    person = Person("John", "Smith")
    assert person.firstname == "John"
    assert person.lastname == "Smith"


def test_equality():
    assert EntityDescription() == EntityDescription()
    assert EntityDescription("name") == EntityDescription("name")

    assert EntityDescription(description="abc") != EntityDescription()
    assert EntityDescription("a") != EntityDescription("b")


# TEST FROM METHODS #
import pytest
from koalak.descriptions import EntityDescription, FieldDescription


def test_entity_description_from_yaml(tmp_path):
    yaml_content = """
    name: test_entity
    description: A test entity
    fields:
      field1:
        type: str
      field2:
        type: int
        kw_only: true
    """

    tmp_file_path = tmp_path / "test_entity.yaml"
    tmp_file_path.write_text(yaml_content)

    entity = EntityDescription.from_yaml(tmp_file_path)

    assert entity.name == "test_entity"
    assert entity.description == "A test entity"

    assert len(entity) == 2
    assert entity["field1"].type is str
    assert entity["field2"].type is int
    assert entity["field2"].kw_only is True


def test_pretty_name_and_plural_name():
    e = EntityDescription("tag")
    assert e.name == "tag"
    assert e.pretty_name == "tag"
    assert e.plural_name == "tags"

    e = EntityDescription("category", plural_name="categories")
    assert e.name == "category"
    assert e.pretty_name == "category"
    assert e.plural_name == "categories"

    e = EntityDescription("test_test")
    assert e.name == "test_test"
    assert e.pretty_name == "test test"
    assert e.plural_name == "test_tests"
