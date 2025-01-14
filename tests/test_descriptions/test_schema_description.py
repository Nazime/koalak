from xml.dom.minidom import Entity

import pytest
from koalak.descriptions import EntityDescription, FieldDescription, SchemaDescription


def test_conception_add_entity():
    schema = SchemaDescription()

    assert len(schema) == 0

    entity_persons = schema.add_entity("persons")

    assert len(schema) == 1
    assert schema["persons"] is entity_persons

    entity_animals = schema.add_entity("animals")
    assert len(schema) == 2
    assert schema["animals"] is entity_animals

    assert list(schema) == [entity_persons, entity_animals]

    with pytest.raises(ValueError):
        schema.add_entity("persons")  # name already exists


def test_conception_add_entity_from_cls_empty_cls_with_name():
    schema = SchemaDescription()

    assert len(schema) == 0

    class Person:
        pass

    entity_persons = schema.add_entity_from_cls(Person, name="persons")
    assert entity_persons.cls is Person
    assert entity_persons.cls_name == "Person"
    assert entity_persons.name == "persons"

    assert len(schema) == 1
    assert schema["persons"] is entity_persons


def test_conception_add_entity_from_cls_empty_cls_without_name():
    schema = SchemaDescription()

    assert len(schema) == 0

    class Person:
        pass

    entity_persons = schema.add_entity_from_cls(Person)
    assert entity_persons.cls is Person
    assert entity_persons.cls_name == "Person"
    assert entity_persons.name == "Person"

    assert len(schema) == 1
    assert schema["Person"] is entity_persons


def test_conception_add_entity_from_cls_with_fields():
    schema = SchemaDescription()

    assert len(schema) == 0

    class Person:
        firstname = FieldDescription()
        lastname: str = FieldDescription()

    entity_persons = schema.add_entity_from_cls(Person, name="persons")
    assert entity_persons.cls is Person
    assert entity_persons.cls_name == "Person"
    assert entity_persons.name == "persons"

    assert len(schema) == 1
    assert schema["persons"] is entity_persons

    assert len(entity_persons) == 2
    firstname_field = entity_persons["firstname"]
    assert firstname_field.annotation is None

    lastname_field = entity_persons["lastname"]
    assert lastname_field.annotation is str


def test_conception_with_2_class_with_generic_fields():
    schema = SchemaDescription()
    assert len(schema) == 0

    class Person:
        firstname = FieldDescription()
        lastname: str = FieldDescription()

    class Animal:
        name: str = FieldDescription()
        owner: Person = FieldDescription()

    entity_persons = schema.add_entity_from_cls(Person, name="persons")
    entity_animals = schema.add_entity_from_cls(Animal, name="animals")

    assert entity_persons.cls is Person
    assert entity_persons.cls_name == "Person"
    assert entity_persons.name == "persons"
    assert len(entity_persons) == 2

    assert entity_animals.cls is Animal
    assert entity_animals.cls_name == "Animal"
    assert entity_animals.name == "animals"
    assert len(entity_animals) == 2
    assert entity_animals["owner"].annotation is Person


def test_schema_description_from_folder():
    pass
    # TODO: implement me


def test_allowed_tags_and_categories():
    # Test without restrictions nothing is raised
    schema = SchemaDescription()
    schema.add_existing_entity(EntityDescription("a"))
    schema.add_existing_entity(EntityDescription("b", category="test"))
    schema.add_existing_entity(EntityDescription("c", tags=["web"]))

    schema = SchemaDescription(allowed_tags=["web"], allowed_categories=["test"])
    schema.add_existing_entity(EntityDescription("a"))
    schema.add_existing_entity(EntityDescription("b", category="test"))
    schema.add_existing_entity(EntityDescription("c", tags=["web"]))
    with pytest.raises(ValueError):
        # Tag techno unkown and should be raised
        schema.add_existing_entity(EntityDescription("d", tags=["techno"]))

    with pytest.raises(ValueError):
        # Tag techno unkown and should be raised
        schema.add_existing_entity(EntityDescription("f", category="cooking"))


def test_filter_with_allowed_tags_and_categories():
    # Create the entities to be added
    entities = [
        EntityDescription("a"),
        EntityDescription("b", category="test"),
        EntityDescription("c", tags=["web"]),
        EntityDescription("d", tags=["techno"]),
        EntityDescription("e", category="cooking", tags=["web"]),
    ]

    # Initialize a schema with allowed tags and categories
    schema = SchemaDescription(
        allowed_tags=["web", "techno"], allowed_categories=["test", "cooking"]
    )

    # Add the entities to the schema
    for entity in entities:
        schema.add_existing_entity(entity)

    # Use filter with allowed tag "web"
    assert [e.name for e in schema.filter(tags="web")] == ["c", "e"]
    assert [e.name for e in schema.filter(tags=["web", "techno"])] == ["c", "d", "e"]

    # Use filter with allowed category "test"
    assert [e.name for e in schema.filter(category="test")] == ["b"]

    # Filtering with an unregistered tag
    with pytest.raises(ValueError):
        schema.filter(tags="unknown_tag")

    # Filtering with an unregistered category
    with pytest.raises(ValueError):
        schema.filter(category="unknown_category")


def test_schema_update():
    schema = SchemaDescription()
    entity_client = EntityDescription("client")
    entity_client.add_field("name", type=str)

    entity_mission = EntityDescription("mission")
    entity_mission.add_field("client", type=entity_client)

    schema.add_existing_entity(entity_client)
    schema.add_existing_entity(entity_mission)
    schema.update()

    assert "missions" in entity_client
    field_missions = entity_client["missions"]
    assert field_missions.atomic_type is entity_mission
