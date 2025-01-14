from typing import Any

from koalak.descriptions import EntityDescription


def feed_parser(parser, attributes: EntityDescription):
    group_filter = parser.add_group("Filter")
    group_negative_filter = parser.add_group("Negative filter")
    parser.add_argument(f"--search", group=group_filter)
    if isinstance(attributes, EntityDescription):
        for attribute in attributes:
            parser.add_argument(f"--{attribute.name}", nargs="*", group=group_filter)
            parser.add_argument(
                f"--no--{attribute.name}", nargs="*", group=group_negative_filter
            )


def getitem(obj: Any, key: str, default: Any = None):
    """
    Retrieve an attribute from an object or a value from a dictionary.

    Args:
        obj (object or dict): The object or dictionary to retrieve the value from.
        key (str): The attribute name or dictionary key.
        default (any, optional): The default value to return if the key is not found. Defaults to None.

    Returns:
        any: The value of the attribute or dictionary key, or the default value.
    """
    if isinstance(obj, dict):
        return obj.get(key, default)
    else:
        return getattr(obj, key, default)


def setitem(obj: Any, key: str, value: Any):
    """
    Set an attribute on an object or a value in a dictionary.

    Args:
        obj (object or dict): The object or dictionary to set the value on.
        key (str): The attribute name or dictionary key.
        value (any): The value to set.

    Returns:
        None
    """
    if isinstance(obj, dict):
        obj[key] = value
    else:
        setattr(obj, key, value)


def get_fields_from_object(item):
    if isinstance(item, dict):
        return list(item.keys())
    else:
        raise ValueError("Flemme d implem la fonction")


def get_fields_from_list_of_dict(l):
    fields = {}
    for item in l:
        for key in get_fields_from_object(item):
            if key not in fields:
                fields[key] = None

    return list(fields.keys())


def print_table(
    objects,
    column_names=None,
    show_lines=None,
    title=None,
    list_join=None,
    add_index=False,
):
    # FIXME: add sort options
    if show_lines is None:
        show_lines = True
    if list_join is None:
        list_join = ", "

    if column_names is None:
        column_names = get_fields_from_list_of_dict(objects)

    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title=title, show_lines=show_lines)

    # Add columns to the table
    if add_index:
        table.add_column("i")

    for column_name in column_names:
        table.add_column(column_name)

    # Add rows to the table
    for i, obj in enumerate(objects, 1):
        row = []
        if add_index:
            row.append(str(i))
        for column_name in column_names:
            cell = getitem(obj, column_name)
            if cell is None:
                cell = ""
            elif isinstance(cell, list):
                cell = list_join.join(map(str, cell))
            row.append(str(cell))
        table.add_row(*row)

    console.print(table)
