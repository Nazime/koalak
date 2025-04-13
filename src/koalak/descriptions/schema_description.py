import re
import typing
from pathlib import Path
from typing import Dict, Iterator, List, Union

import attrs
import rich
from koalak import containers
from koalak.utils.decorators import optionalargs

from .entity_description import EntityDescription, FieldDescription


def camel_to_snake(name):
    # TODO: check this code
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


ATTR_METADATA_KEY = "relationaldb"
HANDLED_TYPES = [str, int, float, bool]


class SchemaDescription:
    """Describe how different EntityDescription are related"""

    def __init__(
        self,
        allowed_tags: list[str] = None,
        allowed_categories: list[str] = None,
        metadata: dict = None,
    ):
        if metadata is None:
            metadata = {}
        self.allowed_tags = allowed_tags
        self.allowed_categories = allowed_categories
        self.metadata = metadata

        self._initialized = False
        self._entities: Dict[str, EntityDescription] = {}
        self._map_cls_name_to_entity: Dict[str, EntityDescription] = {}
        self._map_cls_to_entity: Dict[typing.Type : EntityDescription] = {}

    # TODO: rethink about initialized
    # TODO: add lock function? to lock the attribute in read only? (instead of init)
    # TODO: add warm functionthat will set attributes for speed
    def _check_initialized(self):
        if self._initialized:
            raise ValueError(f"Can not add new entities to already initialize class")

    def add_entity(self, name: str, description: str = None):
        self._check_initialized()
        if name in self._entities:
            raise ValueError(f"Entity {name!r} already exists")

        entity = EntityDescription(name=name, description=description)
        self._entities[name] = entity
        return entity

    def add_existing_entity(self, entity: EntityDescription):
        if entity.name is None:
            raise ValueError(f"entity.name must not be None")

        if entity.name in self._entities:
            raise ValueError(f"Entity {entity.name!r} already exists")

        self._check_entity(entity)
        self._entities[entity.name] = entity
        return entity

    def add_entity_from_cls(self, cls, name=None, description=None):
        # FIXME: add description and other attributes?
        self._check_initialized()
        if name is None:
            name = cls.__name__

        if name in self._entities:
            raise ValueError(f"Entity {name!r} already exists")

        entity = EntityDescription(
            name=name, cls=cls, description=description, cls_name=cls.__name__
        )
        # Adding fields
        generic_fields = {
            attr_name: getattr(cls, attr_name)
            for attr_name in cls.__dict__
            if isinstance(getattr(cls, attr_name), FieldDescription)
        }
        for field_name, field in generic_fields.items():
            field = field.copy()
            field.name = field_name
            if hasattr(cls, "__annotations__") and field_name in cls.__annotations__:
                field.annotation = cls.__annotations__[field_name]
            entity.add_existing_field(field)

        self._check_entity(entity)
        self._entities[name] = entity
        # TODO: add mapping in other methods
        self._map_cls_to_entity[cls] = entity
        return entity

    def filter(self, tags=None, category=None, **kwargs) -> Iterator[EntityDescription]:
        if self.allowed_tags and tags:
            _tags = tags
            if not isinstance(tags, list):
                _tags = [tags]
            for tag in _tags:
                if tag not in self.allowed_tags:
                    raise ValueError(f"Can not search for unregistred tag '{tag}'")

        if self.allowed_categories and category:
            _category = category
            if not isinstance(category, list):
                _category = [category]
            for c in _category:
                if c not in self.allowed_categories:
                    raise ValueError(f"Can not search for unregistred category '{c}'")

        return containers.search(self, tags=tags, category=category, **kwargs)

    def __iter__(self) -> Iterator[EntityDescription]:
        yield from self._entities.values()

    def __len__(self):
        return self._entities.__len__()

    def __getitem__(self, item):
        return self._entities.__getitem__(item)

    @optionalargs(firstarg=str)
    def entity(self, cls, entity_name: str = None, *, description: str = None):
        if entity_name is None:
            entity_name = cls.__name__

        entity = self.add_entity_from_cls(
            cls, name=entity_name, description=description
        )
        attrs_cls = entity.build_attrs_dataclass(name=cls.__name__)
        entity.cls = attrs_cls
        return attrs_cls

    @optionalargs(firstarg=str)
    def entity2(self, cls, entity_name: str = None, *, description: str = None):
        """Register new entity"""
        # FIXME: if entity name match keyword! keep keyword and entity will be accesible trhoug [] syntax
        # FIXME: study the case if the entity is already built

        self._check_initialized()
        # ======================================= #
        # decorate cls with attr (if not already) #
        # ======================================= #
        if entity_name is None:
            entity_name = cls.__name__
        if not hasattr(cls, "__attrs_attrs__"):
            # TODO: adding slots is False, so that we can dynamically add attributes to our class!
            #       we can simply ad the attribute `id` so that we don't need slots?
            cls = attrs.define(cls, slots=False)

            current_entity = EntityDescription(
                name=entity_name,
                cls=cls,
                cls_name=cls.__name__,
                attribute_name=camel_to_snake(cls.__name__),
                description=description,
            )
            self.entities[entity_name] = current_entity

            # add attributes
            current_attributes = current_entity.attributes
            for attr_attribute in cls.__attrs_attrs__:
                # Add annotation for autocomplete
                attr_attribute: attrs.Attribute

                required = attr_attribute.default is attrs.NOTHING
                relationaldb_attr_metadata = attr_attribute.metadata.get(
                    ATTR_METADATA_KEY, {}
                )

                current_attributes[attr_attribute.name] = FieldDescription(
                    attr_attribute.name,
                    annotation=attr_attribute.type,
                    kw_only=attr_attribute.kw_only,
                    required=required,
                    default=attr_attribute.default,
                    **relationaldb_attr_metadata,
                )

        else:
            raise ValueError(
                f"Class {cls.__name__} must not be decorated with attrs.define use db.define instead!"
            )

        return cls

    define = entity

    def init(self):
        """

        List of checks
        - Conception not initilaised twice
        - Check all type are handled
            - primitives types
            - list/set ...
            - known entity
        - All entities must have an attrs class
        """

        # Check that class is not already initialised
        if self._initialized:
            raise ValueError(f"Already initialized")
        self._initialized = True

        # Adding classes for each entity (if it doesn't have)
        for entity in self:
            if entity.cls is None:
                entity.cls = entity.build_attrs_dataclass()
                entity.cls_name = entity.cls.__name__

        # Add cls mapping
        for entity in self:
            self._map_cls_name_to_entity[entity.cls_name] = entity
            self._map_cls_to_entity[entity.cls] = entity

        # Get classes
        classes = [e.cls for e in self]

        # Compute referenced_entity
        for entity in self:
            for field in entity:
                if typing.get_origin(field.annotation) not in [dict, list, None]:
                    pass

                if field.annotation is None:
                    continue
                elif field.annotation in HANDLED_TYPES:
                    continue
                elif isinstance(field.annotation, str):
                    if field.annotation in self._entities:
                        field.referenced_entity = self._entities[field.annotation]
                        field.annotation = field.referenced_entity.cls
                    else:
                        pass  # FIXME: raise value error
                elif not field.is_atomic() and typing.get_origin(field.annotation) in [
                    dict,
                    list,
                    set,
                ]:
                    continue
                # TODO: here, we have to handle List[] Set[] ...
                else:  # field.annotation is a cls
                    cls_name = field.annotation.__name__
                    if cls_name not in self._map_cls_name_to_entity:
                        raise ValueError(
                            f"Unregistred/Unhandled annotation for field {entity.name}.{field.name}: {field.annotation}"
                        )
                    referenced_entity = self._map_cls_name_to_entity[cls_name]
                    field.referenced_entity = referenced_entity

    @classmethod
    def from_yaml(cls, filepath: Union[str, Path]):
        import yaml

        # Open the YAML file and load its content as a dictionary
        with open(filepath) as yaml_file:
            data = yaml.safe_load(yaml_file)

        return cls.from_dict(data)

    @classmethod
    def from_folder(
        cls,
        filepath: Union[str, Path],
        allowed_tags=None,
        allowed_categories=None,
        update: bool = None,
        metadata: dict = None,
    ) -> "SchemaDescription":

        schema = SchemaDescription(
            allowed_tags=allowed_tags, allowed_categories=allowed_categories
        )

        schema.add_entities_from_folder(filepath, update=update, metadata=metadata)
        return schema

    def add_entities_from_folder(self, filepath, update=None, metadata=None):
        if update is None:
            update = True
        if metadata is None:
            metadata = {}

        folder_path = Path(filepath)

        if not folder_path.is_dir():
            raise ValueError(f"Provided path '{folder_path}' is not a directory.")

        for file_path in folder_path.rglob("*"):
            if file_path.is_dir():
                continue
            entity = EntityDescription.from_file(file_path, ignore_type_error=True)
            entity.metadata.update(metadata)
            self.add_existing_entity(entity)

        if update:
            self.update_referenced_entities_from_str()
            self.update()

    @classmethod
    def from_dict(
        cls,
        entities_dict: Dict,
        init=None,
        ignore_entity_keys=None,
        replace_entity_keys=None,
        replace_field_keys=None,
    ):
        if ignore_entity_keys is None:
            ignore_entity_keys = []

        if replace_entity_keys is None:
            replace_entity_keys = {}

        if replace_field_keys is None:
            replace_field_keys = {}

        if init is None:
            init = True

        conception = Conceptor()
        for entity_name, entity_dict in entities_dict.items():
            # Remove ignored keys
            for key in ignore_entity_keys:
                entity_dict.pop(key, None)

            # Rename keys
            for old_name, new_name in replace_entity_keys.items():
                if old_name in entity_dict:
                    entity_dict[new_name] = entity_dict.pop(old_name)

            fields_dict = entity_dict.pop("fields")
            current_entity = conception.add_entity(entity_name, **entity_dict)

            for field_name, field_dict in fields_dict.items():
                # Rename keys
                for old_name, new_name in replace_field_keys.items():
                    if old_name in field_dict:
                        field_dict[new_name] = field_dict.pop(old_name)

                if "type" in field_dict:
                    field_dict["type"] = cls._str_annotation_to_annotation(
                        field_dict["type"]
                    )

                if field_dict.get("is_set"):
                    field_dict.pop("is_set")
                    if field_dict.get("type"):
                        field_dict["type"] = typing.Set[field_dict["type"]]
                    else:
                        field_dict["type"] = typing.Set

                # FIXME: same with list

                current_entity.add_field(field_name, **field_dict)

        if init:
            conception.init()
        return conception

    @classmethod
    def from_csv_folder(self, folder_path: str):
        folder_path = Path(folder_path)

        conception = Conceptor()
        for path in folder_path.glob("*.csv"):
            entity = EntityDescription.from_csv(path)
            conception.add_existing_entity(entity)

        return conception

    def update_referenced_entities_from_str(self):
        map_str_name_to_entity = {}
        for entity in self:
            map_str_name_to_entity[entity.name] = entity
        for entity in self:
            for field in entity:
                if isinstance(field.type, str):
                    if field.type not in map_str_name_to_entity:
                        raise ValueError(
                            f'Unknown referenced entity {entity.name}.{field.name} type "{field.type}"'
                        )
                    field.type = map_str_name_to_entity[field.type]
                elif field.is_set() and isinstance(field.atomic_type, str):
                    if field.atomic_type not in map_str_name_to_entity:
                        raise ValueError(
                            f'Unknown referenced entity {entity.name}.{field.name} type "{field.type}"'
                        )
                    field.type = set[map_str_name_to_entity[field.atomic_type]]

    def update(self):
        # Check related_fields
        #  Create related fields in the entities
        for entity in self:
            for field in entity:
                # ignore related fields => ex host.services
                if field.is_linked_by_related_name:
                    continue

                if field.has_relationship():
                    referenced_entity = field.referenced_entity
                    # for example if "services" not in "host"
                    # related_field = host.services; field = service.host
                    if field.related_name not in referenced_entity:
                        related_field = FieldDescription(
                            field.related_name,
                            type=set[entity],
                            hidden_in_list=True,
                            is_linked_by_related_name=True,
                        )
                        referenced_entity.add_existing_field(related_field)
                    else:
                        related_field = referenced_entity[field.related_name]
                        if related_field.atomic_type is not entity:
                            raise ValueError(
                                f"related_name '{field.related_name}' is not of the expected type '{entity}'."
                                f"Maby the entity have more than 1 related fields of the same type, you need "
                                f"to explicitly set the related name"
                            )

                    pass

            # Check pretty_id_fields if exist in entity fields
            entity_fields_names = [field.name for field in entity]
            if not all(f in entity_fields_names for f in entity.pretty_id_fields):
                raise ValueError(
                    f"pretty_id_fields items of '{entity}' should all exist in the entity fields."
                )

    def cls_to_entity(self, cls: typing.Type) -> EntityDescription:
        return self._map_cls_to_entity[cls]

    def to_json(self) -> Dict:
        return {entity.name: entity.to_json() for entity in self}

    def to_yaml(self, filepath: str) -> None:
        import yaml

        dict_description = self.to_json()

        with open(filepath, "w") as yaml_file:
            yaml.dump(dict_description, yaml_file, sort_keys=False)

    def rich_print(self):
        for entity in self:
            entity.rich_print()

    def print_warnings(self):
        """Print warnings for bad designs of fields"""
        for entity in self:
            for field in entity:
                if (
                    field.in_filter_query
                    and not field.indexed
                    and not field.unique
                    and not field.has_relationship()
                ):
                    rich.print(
                        f"WARNING: '{entity.name}.{field.name}' in_filter_query and no indexed"
                    )

    def _check_entity(self, entity: EntityDescription):
        if self.allowed_tags and entity.tags:
            for tag in entity.tags:
                if tag not in self.allowed_tags:
                    raise ValueError(
                        f"Tag '{tag}' for entity '{entity.name}' not allowed in this schema"
                    )

        if (
            self.allowed_categories
            and entity.category
            and entity.category not in self.allowed_categories
        ):
            raise ValueError(
                f"Category '{entity.category}' for entity '{entity.name}' not allowed in this schema"
            )

    def sort(self):
        self._entities = {e.name: e for e in sorted(self, key=lambda x: x.order)}

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._entities
        raise NotImplemented("Can check only str")
