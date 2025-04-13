from pathlib import Path
from typing import Iterator, Union

import attrs

from .field_description import FieldDescription


class EntityDescription:
    DEFAULT_ORDER = 50
    BANNED_PRETTY_ID_CHARS = ["/", "\\", "?", "#", "%", "-"]
    BANNED_PRETTY_ID_SEPARATORS = BANNED_PRETTY_ID_CHARS + [" "]

    def __init__(
        self,
        name: str = None,
        *,
        pretty_name: str = None,
        plural_name: str = None,
        pretty_id_fields: list[str] = None,
        pretty_id_fields_separator: list[str] = None,
        cls_name: str = None,
        cls=None,
        title: str = None,
        description: str = None,
        extra: dict = None,
        unique=None,
        category: str = None,
        tags: list[str] = None,
        order: int = None,
        metadata: dict = None,
    ):
        if metadata is None:
            metadata = {}
        if extra is None:
            extra = {}

        if unique is None:
            unique = []

        if order is None:
            order = self.DEFAULT_ORDER

        if tags is None:
            tags = []
        elif isinstance(tags, str):
            tags = [tags]

        # cast pretty id to list of strings
        if pretty_id_fields is None:
            pretty_id_fields = []
        elif isinstance(pretty_id_fields, str):
            pretty_id_fields = [pretty_id_fields]

        # set default pretty_id_fields_separator and check its validity
        if pretty_id_fields_separator is None:
            pretty_id_fields_separator = "_"
        elif len(pretty_id_fields_separator) > 1:
            raise ValueError(
                "pretty_id_fields_separator must be only one character long"
            )
        elif pretty_id_fields_separator in self.BANNED_PRETTY_ID_SEPARATORS:
            raise ValueError(
                f"pretty_id_fields_separator must not be in {self.BANNED_PRETTY_ID_SEPARATORS}"
            )

        self.name: str = name
        self.cls_name: str = cls_name
        self.cls = cls
        self.title: str = title
        self.description: str = description
        self.extra = extra
        self.unique = unique
        self.order = order
        self.category = category
        self.tags = tags
        self.metadata = metadata
        self._fields = {}
        self._pretty_name = pretty_name
        self._plural_name = plural_name
        self.pretty_id_fields = pretty_id_fields
        self.pretty_id_fields_separator = pretty_id_fields_separator

    @property
    def pretty_name(self):
        if self._pretty_name is None and self.name:
            return self.name.replace("_", " ")
        return self._pretty_name

    @property
    def plural_name(self):
        if self._plural_name is None and self.name:
            return self.name + "s"
        return self._plural_name

    @property
    def repr_fields(self) -> list[FieldDescription]:
        """
        returns list of fields included in the string representation of the model
        (fields with in_filter_query).
        """
        return [field for field in self._fields.values() if field.in_filter_query]

    def __iter__(self) -> Iterator[FieldDescription]:
        yield from self._fields.values()

    def __len__(self):
        return self._fields.__len__()

    def __getitem__(self, item) -> FieldDescription:
        return self._fields.__getitem__(item)

    def __repr__(self):
        name = self.name
        if name is None:
            name = ""
        return f"Entity({name})"

    def __eq__(self, other):
        if isinstance(other, EntityDescription):
            return (
                self.name == other.name
                and self.cls_name == other.cls_name
                and self.cls == other.cls
                and self.description == other.description
                and self._fields == other._fields
            )

        return False

    def __contains__(self, item):
        if isinstance(item, str):
            return item in self._fields
        raise NotImplemented("Can check only str")

    def add_field(self, name: str, *args, **kwargs):
        if name in self._fields:
            raise ValueError(f"Field {name!r} already exists")

        field = FieldDescription(name=name, entity=self, *args, **kwargs)
        self._fields[name] = field
        return field

    def add_existing_field(self, field: FieldDescription):
        if field.name is None:
            raise ValueError(f"field.name must not be None")

        if field.name in self._fields:
            raise ValueError(f"Field {field.name!r} already exists")

        # if field.entity:
        #    raise ValueError("Can not add field with already linked entity")

        # TODO: what if the generic_field is changed afterward?
        self._fields[field.name] = field
        field.entity = self
        return field

    def field_name_in(self, name: str):
        return name in self._fields

    @property
    def fields(self):
        return list(self)

    def get_fields(self, kw_only=None):
        raise NotImplemented

    def get_kw_only_attributes(self):
        return [e for e in self if e.kw_only]

    def get_not_kw_only_attributes(self):
        return [e for e in self if not e.kw_only]

    def get_in_filter_query_attributes(self):
        return [e for e in self if e.in_filter_query]

    def get_not_in_filter_query_attributes(self):
        return [e for e in self if not e.in_filter_query]

    # TODO: remove following functions!
    @property
    def snakecase_name(self):
        return camel_to_snake(self.cls_name)

    @property
    def camlecase_name(self):
        return self.cls_name

    @property
    def container_name(self):
        return f"{self.cls_name}Container"

    @property
    def normalize_func_name(self):
        return f"_normalize_{self.snakecase_name}"

    @property
    def fromdict_name(self):
        return f"fromdict_{self.snakecase_name}"

    @property
    def is_feedable(self):
        for field in self:
            if field.in_filter_query:
                return True

        return False

    def build_attrs_dataclass(self, name=None):
        if name is None:
            name = self.name
        attributes = {}
        for field in self:
            attributes[field.name] = field.build_attrs_field()

        AttrClass = type(name, (object,), attributes)
        return attrs.define(AttrClass)

    def to_json(self):
        return {"fields": {field.name: field.to_json() for field in self}}

    @classmethod
    def from_dict(
        cls, dico: dict, type_as_str=None, default_name=None, ignore_type_error=None
    ) -> "EntityDescription":
        # Create a copy
        dico = dict(dico)
        if "name" not in dico:
            dico["name"] = default_name
        fields = dico.pop("fields")
        entity = EntityDescription(**dico)
        for field_name, field_attribute in fields.items():
            new_field = FieldDescription.from_dict(
                field_attribute,
                type_as_str=type_as_str,
                ignore_type_error=ignore_type_error,
            )
            new_field.name = field_name
            entity.add_existing_field(new_field)
        return entity

    @classmethod
    def from_file(
        cls, filepath: Union[str, Path], ignore_type_error=None
    ) -> "EntityDescription":
        path = Path(filepath)
        default_name = path.stem
        if path.suffix.lower() in [".yaml", ".yml"]:
            return cls.from_yaml(
                filepath, default_name=default_name, ignore_type_error=ignore_type_error
            )
        elif path.suffix.lower() == ".csv":
            return cls.from_csv(filepath)
        else:
            raise ValueError(f"Unsupported file type: {path}")

    @classmethod
    def from_yaml(
        cls, filepath: Union[str, Path], default_name=None, ignore_type_error=None
    ) -> "EntityDescription":
        import yaml

        with open(filepath, "r") as file:
            data = yaml.safe_load(file)
            return cls.from_dict(
                data,
                type_as_str=True,
                default_name=default_name,
                ignore_type_error=ignore_type_error,
            )

    @classmethod
    def from_csv(cls, filepath: str, *, entity_name: str = None):
        import csv

        if entity_name is None:
            entity_name = Path(filepath).stem

        entity = EntityDescription(entity_name)
        with open(filepath) as csvfile:
            csvreader = csv.reader(csvfile)
            headers = next(csvreader)
            for header in headers:
                entity.add_field(header)
        return entity

    def rich_print(self):
        from rich import print
        from rich.console import Group
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text

        entity_content = []

        if self.description:
            entity_content.append(Text(self.description, style="bold cyan"))

        if self.metadata:
            table = Table(show_header=False, box=None, pad_edge=False)
            for key, value in self.metadata.items():
                table.add_row(
                    Text(f"{key}:", style="bold yellow"),
                    Text(str(value), style="white"),
                )
            entity_content.append(
                Panel(
                    table, title="Metadata", title_align="left", border_style="yellow"
                )
            )

        if self.tags:
            entity_content.append(
                Text(f"Tags: {', '.join(self.tags)}", style="bold green")
            )

        # Add fields inside the panel with correct styling
        for field in self:
            field_text = Text(f"  - {field.name} ", style="white")
            field_text.append(f"({field.description})", style="dim")
            entity_content.append(field_text)

        entity_panel = Panel(
            Group(*entity_content),
            title=f"[bold magenta]{self.name}[/bold magenta]",
            expand=False,
        )

        print(entity_panel)
