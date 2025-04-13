# TODO: try implementing an argparse formatter instead?
import typing
from typing import Any, Dict

if typing.TYPE_CHECKING:
    from .subcommand_parser import SubcommandParser
from koalak.descriptions import EntityDescription, FieldDescription

# import rich
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# RICH STYLE CONSTS
STYLE_USAGE = "yellow bold"
# table
STYLE_OPTIONS_TABLE_SHOW_LINES = False
STYLE_OPTIONS_TABLE_LEADING = 0
STYLE_OPTIONS_TABLE_PAD_EDGE = False
STYLE_OPTIONS_TABLE_PADDING = (0, 1)
STYLE_OPTIONS_TABLE_BOX = ""
STYLE_OPTIONS_TABLE_ROW_STYLES = None
STYLE_OPTIONS_TABLE_BORDER_STYLE = None

STYLE_ARGUMENTS_NAME = "bold cyan"
STYLE_OPTIONS_TYPE = "yellow bold"

console = Console()


types_to_text = {
    int: "INTEGER",
    str: "TEXT",
    bool: "",
}


def print_help(cmd: "SubcommandParser"):
    SubcommandPrinter(cmd).print_help()


class SubcommandPrinter:
    def __init__(self, cmd: "SubcommandParser"):
        self.cmd = cmd

    def print_entity(
        self, entity: EntityDescription, *, first_cell_width, add_type=None
    ):
        if add_type is None:
            add_type = True
        # If entity is empty do nothing
        fields = [e for e in entity if not e.hidden]
        if not fields:
            return
        rich_table = self._get_rich_table()
        for element in fields:
            self._add_row_argument(rich_table, element, add_type=add_type)

        rich_table.columns[0].width = first_cell_width + 4  # Adding few spaces
        # TODO if commands do not need second thing
        # rich_table.columns[1].width = 15

        if entity.description:
            description = entity.description + "\n"
            rich_group = Group(description, rich_table)
        else:
            rich_group = rich_table

        group_panel = Panel(
            rich_group, title=entity.title, border_style="dim", title_align="left"
        )
        console.print(group_panel)

    def _add_row_argument(self, table, argument: FieldDescription, *, add_type):
        # Get name column
        styled_name = Text(argument.display_name, style=STYLE_ARGUMENTS_NAME)

        args = []
        # Get type column
        if add_type:
            if argument.choices:
                str_choices = "[" + ", ".join(argument.choices) + "]"
                str_choices = Text(str_choices, style=STYLE_OPTIONS_TYPE)
                args.append(str_choices)
            else:
                type_str = types_to_text.get(argument.type, "TEXT")
                if argument.many:
                    type_str = f"List[{type_str}]"
                styled_type = Text(type_str, style=STYLE_OPTIONS_TYPE)
                args.append(styled_type)

        # Get help column
        if argument.description is not None:
            help_str = Text(argument.description)
        else:
            help_str = Text()
        if (
            argument.default is not FieldDescription.NOTHING
            and argument.default is not None
        ):
            help_str += Text(f" [default: {argument.default}]", style="dim")
        help_str.plain = help_str.plain.strip()
        args.append(help_str)
        table.add_row(styled_name, *args)

    def _add_row_subcommands(self, table, subcommand: "SubcommandParser"):
        cmd_name = Text(subcommand.name, style=STYLE_ARGUMENTS_NAME)
        table.add_row(cmd_name, subcommand.description)

    def _get_maximum_name_width(self):
        names = []
        for e in self.cmd.positional_arguments:
            names.append(e.display_name)

        for e in self.cmd.optional_arguments:
            names.append(e.display_name)

        for e in self.cmd.subcommands.keys():
            names.append(e)

        if names:
            max_name = max(names, key=len)
            return len(max_name)
        else:
            return 20

    def print_help(self, file=None):
        """Print the help menu with better coloring"""
        # print the following
        # - prolog
        # - usage
        # - description
        # - Groups of arguments (subcommand,s positional args, optional args)

        # FIXME: test/me

        # header prog name and description
        prog = self.cmd.name

        # Print prolog
        # ------------
        if self.cmd.prolog:
            console.print(self.cmd.prolog)

        # Print usage
        # -----------
        console.print(f"[{STYLE_USAGE}]Usage:[/{STYLE_USAGE}] {prog} [-h] <subcommand>")
        console.print()
        # Print description
        # -----------------
        if self.cmd.description:
            console.print(f"{self.cmd.description}")
            console.print()

        # Print all groups
        # ----------------
        self.print_arguments_and_commands()

        # Print epilog
        # ------------
        if self.cmd.epilog:
            console.print(self.cmd.epilog)

    def print_arguments_and_commands(self):
        first_cell_width = self._get_maximum_name_width()

        self.print_entity(
            self.cmd.positional_arguments, first_cell_width=first_cell_width
        )
        for group in self.cmd.commands_groups.values():
            self.print_entity(group, first_cell_width=first_cell_width, add_type=False)
        for group in self.cmd.optional_arguments_groups.values():
            self.print_entity(group, first_cell_width=first_cell_width)

    def _get_rich_table(self):
        t_styles: Dict[str, Any] = {
            "show_lines": STYLE_OPTIONS_TABLE_SHOW_LINES,
            "leading": STYLE_OPTIONS_TABLE_LEADING,
            "box": STYLE_OPTIONS_TABLE_BOX,
            "border_style": STYLE_OPTIONS_TABLE_BORDER_STYLE,
            "row_styles": STYLE_OPTIONS_TABLE_ROW_STYLES,
            "pad_edge": STYLE_OPTIONS_TABLE_PAD_EDGE,
            "padding": STYLE_OPTIONS_TABLE_PADDING,
        }
        table = Table(
            highlight=True,
            show_header=False,
            **t_styles,
        )

        return table
