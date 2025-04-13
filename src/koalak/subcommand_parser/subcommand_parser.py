import argparse
import inspect
import sys
import typing
from typing import Any, Callable, Dict, List, Union

import argcomplete
import rich
from koalak.descriptions import EntityDescription, FieldDescription, SchemaDescription

from .subcommand_printer import print_help

DEFAULT_OPTIONS_GROUP_NAME = "Options Arguments"
DEFAULT_COMMANDS_GROUP_NAME = "Commands"


def generic_print(obj):
    if obj is None:
        return
    if isinstance(obj, dict):
        rich.print(obj)

    elif isinstance(obj, typing.Iterable):
        for e in obj:
            print(e)
    else:
        rich.print(obj)


def argparse_argument_to_field_description(
    argparse_action, choices=None
) -> FieldDescription:
    dest = argparse_action.dest
    help = argparse_action.help
    extra_kwargs = {}
    if argparse_action.option_strings == []:
        required = True
        name = dest
        display_name = name
        is_option = False
    else:
        required = False
        display_name = " ".join(argparse_action.option_strings)
        args_with_long_name = [
            e for e in argparse_action.option_strings if e.startswith("--")
        ]
        if args_with_long_name:
            name = args_with_long_name[0][2:]  # remove --
        else:
            name = argparse_action.option_strings[0][1:]
        is_option = True

    if argparse_action.type is None:
        type = str
    else:
        type = argparse_action.type

    if isinstance(argparse_action, argparse._StoreTrueAction):
        default = False
        type = bool
    elif isinstance(argparse_action, argparse._StoreFalseAction):
        type = bool
        default = True
    else:
        default = argparse_action.default

    if default == "==SUPPRESS==":
        default = None

    if required and default is None:
        pass
    else:
        extra_kwargs["default"] = default

    if argparse_action.nargs in ["*", "+"]:
        args_as_list = True
    else:
        args_as_list = False

    return FieldDescription(
        name=name,
        display_name=display_name,
        description=help,
        required=required,
        type=type,
        many=args_as_list,
        kw_only=is_option,
        dest=dest,
        choices=choices,
        **extra_kwargs,
    )


class SubcommandParser:
    def __init__(
        self,
        prog: str = None,
        *,
        parent: "SubcommandParser" = None,
        autocomplete: bool = None,
        # Help
        prolog: str = None,
        description: str = None,
        epilog: str = None,
        # private params
        _parser=None,
        _depth: int = None,
    ):
        """
        Args:
            prog: name of the program
            parent: parent parser
            _parser: argparse.ArgParser to use
            description: description of the program
            autocomplete: E,able autocomplete

        Advantages over argparse:
            - use add_subcommand instead of using add_parsers then add_subparser
            - run command that will run directly the program
            - better help with groups/colors
            - create parsers/commands from functions/methods
            - [poc] ease of use autocomplete
        """
        # Normalize arguments #
        # ------------------- #
        if prog is None:
            prog = sys.argv[0]

        if autocomplete is None:
            autocomplete = False

        if _depth is None:
            _depth = 1
        # SubcommandParser specific attributes
        # TODO: double check public/private attributes!
        self.positional_arguments = EntityDescription(title="Positional Arguments")
        self.optional_arguments = EntityDescription()
        self.subcommands: Dict[str, SubcommandParser] = {}
        self.function = None  # function to run
        self.autocomplete = autocomplete

        # Groups for help
        # Separate effective commands/arguments from groupes_commands/arguments
        # as effective are unique across all the SubcommandParser but groups not
        self.optional_arguments_groups: Dict[str, EntityDescription] = {
            DEFAULT_OPTIONS_GROUP_NAME: EntityDescription(
                title=DEFAULT_OPTIONS_GROUP_NAME
            )
        }
        self.commands_groups: Dict[str, EntityDescription] = {
            DEFAULT_COMMANDS_GROUP_NAME: EntityDescription(
                title=DEFAULT_COMMANDS_GROUP_NAME
            )
        }

        # Argparse related attributes
        self.parent = parent
        self.name = prog or sys.argv[0]
        self.description = description
        self.prolog = prolog
        self.epilog = epilog

        # private attributes
        self._argparse_subparsers = None

        # Help related attributes
        self._i_group_name = 0

        if self.parent is None:
            self.fullname = self.name
        else:
            self.fullname = f"{self.parent.fullname}.{self.name}"

        if _parser is None:
            _parser = argparse.ArgumentParser(
                prog=prog, description=description, epilog=epilog
            )

        self._subcommand_depth = _depth
        self._argparse_parser = _parser
        self._argparse_parser.print_help = self.print_help
        self._argparse_parser.print_usage = self.print_help

        self._install_rich_traceback()  # FIXME: find better way to call this code?

    # ======== #
    # MAIN API #
    # ======== #

    def add_argument(
        self,
        *args,
        group: Union[str, EntityDescription] = None,
        hide: bool = None,
        **kwargs,
    ):
        """Same as ArgumentParser.add_argument with hide and group params"""
        argparse_arg = self._argparse_parser.add_argument(*args, **kwargs)
        field_description = argparse_argument_to_field_description(
            argparse_arg, choices=kwargs.get("choices")
        )
        field_description.hidden = hide
        self._add_argument_from_field_description(field_description, group=group)

    def _add_argument_from_field_description(
        self, field_description: FieldDescription, group=None
    ):
        if group is None:
            group = DEFAULT_OPTIONS_GROUP_NAME
        elif isinstance(group, EntityDescription):
            group = group.name

        if field_description.kw_only:
            self.optional_arguments.add_existing_field(field_description)
            self.optional_arguments_groups[group].add_existing_field(field_description)
        else:
            if self.subcommands:
                raise ValueError(
                    "Can not have both positional arguments and subcommands"
                )
            self.positional_arguments.add_existing_field(field_description)
            # TODO check that positional arguments do not have groups

    def add_group(
        self, name=None, *, title: str = None, description: str = None
    ) -> EntityDescription:
        """Add group for showing in help (group will be added for both optionals arguments and commands"""
        if name is None:
            name = f"_random_group_koalak_{self._i_group_name}"
            self._i_group_name += 1

        # Since optional_arguments groups and commands groups are syncro, check only one
        if name in self.optional_arguments_groups:
            raise KeyError(f"Group {name} already exists")

        if title is None:
            title = name

        if description is None:
            description = ""

        for dico in [self.optional_arguments_groups, self.commands_groups]:
            group = EntityDescription(name=name, title=title, description=description)
            dico[name] = group

        # Return one of the groups, it's not important which one since they are the same
        return group

    def _add_subcommand_from_existing_cmd(
        self, *, cmd: "SubcommandParser", description, group, hide
    ):
        name = cmd.name
        if hide is None:
            hide = False

        if group is None:
            group = DEFAULT_COMMANDS_GROUP_NAME

        if name in self.subcommands:
            raise KeyError(f"command {name!r} already exists")

        if self.positional_arguments:
            raise ValueError("Can not have both commands and positional arguments")

        cmd.parent = self

        # Add it to group
        cmd_description = FieldDescription(
            name=name, description=description, hidden=hide
        )

        self.commands_groups[group].add_existing_field(cmd_description)
        self.subcommands[name] = cmd

    def add_subcommand(
        self, command_name, description: str = None, group=None, hide: bool = None
    ):
        if command_name in self.subcommands:
            raise KeyError(f"command {command_name!r} already exists")

        self._init_argparse_subparsers()
        cmd_argparse_parser = self._argparse_subparsers.add_parser(command_name)
        cmd = SubcommandParser(
            command_name,
            description=description,
            _depth=self._subcommand_depth + 1,
            _parser=cmd_argparse_parser,
            parent=self,
        )
        # TODO: description exist in 2 diffretn location (cmd.description, and field.description)

        self._add_subcommand_from_existing_cmd(
            cmd=cmd, description=description, group=group, hide=hide
        )
        return cmd

    @classmethod
    def _process_function_for_parser(
        cls,
        *,
        function: Callable,
        cmd: "SubcommandParser",
        default_instance: Any = None,
    ) -> Callable:
        # TODO add more handled types!
        handled_types = {str, int, float, bool, List[str]}
        function_signature = inspect.signature(function)
        function_parameters = dict(function_signature.parameters)
        # TODO: handle bool with store true and store false

        # If default_instance provided remove first param that should be 'self'
        if default_instance is not None:
            if not function_parameters:
                raise ValueError(
                    "The function must have at least one parameter when a default instance is provided"
                )

            # Remove the first param
            first_param = next(iter(function_parameters))
            function_parameters.pop(first_param)

        # Check that all parameters have an annotation and it's handled
        for param_name, param in function_parameters.items():
            if param.annotation is inspect._empty:
                raise ValueError(f"Parameter '{param_name}' must have an annotation")
            elif param.annotation not in handled_types:
                raise TypeError(
                    f"Parameter '{param_name} type '{param.annotation}' not handled"
                )

        for param_name, param in function_parameters.items():
            kwargs_params = {}
            default_value = param.default
            arg_name = param_name

            # Handle if param keyword or positional
            # Keyword only params are always optional argparse
            if param.kind is param.KEYWORD_ONLY:
                param_is_argparse_positional = False
            # Positional only param are always positional argparse
            elif param.kind is param.POSITIONAL_ONLY:
                param_is_argparse_positional = True
            # POSITIONAL_OR_KEYWORD will check the default value
            else:
                # here, param.kind is param.POSITIONAL_OR_KEYWORD
                if default_value is inspect._empty:
                    param_is_argparse_positional = True
                else:
                    param_is_argparse_positional = False

            # Handle default value
            if default_value is not inspect._empty:
                kwargs_params["default"] = default_value
                kwargs_params["required"] = False
            else:
                kwargs_params["required"] = True

            if param.annotation in [List[str]]:
                if kwargs_params["required"]:
                    kwargs_params["nargs"] = "+"
                else:
                    kwargs_params["nargs"] = "*"
                kwargs_params["type"] = typing.get_args(param.annotation)[0]
            else:
                kwargs_params["type"] = param.annotation
            # Last treatment
            if param_is_argparse_positional:
                kwargs_params.pop("required")
            else:
                arg_name = f"--{param_name}"

            # debug(param_name, param, kwargs_params, arg_name)
            cmd.add_argument(arg_name, **kwargs_params)

        # TODO: add functools.wraps but without copying the signature
        def wrapped_function(namespace_args: argparse.Namespace):
            func_args = {k: getattr(namespace_args, k) for k in function_parameters}
            if default_instance is not None:
                result = function(default_instance, **func_args)
            else:
                result = function(**func_args)
            generic_print(result)
            return result

        return wrapped_function

    @classmethod
    def from_function(
        cls,
        function: Callable,
        *,
        name=None,
        default_instance: Any = None,
        _parser=None,
        _depth: int = None,
        parent=None,
    ):
        """Create a SubcommandParser from an existing function

        Args:
            function: function from where to build the args
            default_instance: if a function is a method, give the default instance to run it
        """
        if name is None:
            name = function.__name__
        cmd = SubcommandParser(
            name,
            _parser=_parser,
            _depth=_depth,
            parent=parent,
            description=function.__doc__,
        )
        wrapped_function = cls._process_function_for_parser(
            function=function, cmd=cmd, default_instance=default_instance
        )
        cmd.register_function(wrapped_function)
        return cmd

    def add_subcommand_from_function(
        self,
        function: Callable,
        default_instance: Any = None,
        group=None,
        hide: bool = None,
        description: str = None,
        name=None,
        replace_name_underscrol=None,
    ):
        if replace_name_underscrol is None:
            replace_name_underscrol = True
        if name is None:
            name = function.__name__
            if replace_name_underscrol:
                name = name.replace("_", "-")
        if description is None:
            description = function.__doc__
        self._init_argparse_subparsers()
        cmd_argparse_parser = self._argparse_subparsers.add_parser(name)
        cmd = SubcommandParser.from_function(
            function,
            default_instance=default_instance,
            _depth=self._subcommand_depth + 1,
            _parser=cmd_argparse_parser,
            parent=self,
            name=name,
        )

        self._add_subcommand_from_existing_cmd(
            cmd=cmd, group=group, hide=hide, description=description
        )
        return cmd

    def add_help_subcommand(self, command_name, description=None, group=None):
        """Only add this command in the help

        Explanation:
            this could be useful if you have a lot of commands that are hidden
            and you want to add one help description to group all these commands
        """
        # FIXME
        if group is None:
            group = DEFAULT_COMMANDS_GROUP_NAME

        if command_name in self.subcommands:
            raise KeyError(f"command {command_name!r} already exists")

        if command_name in self._group_namespace:
            raise KeyError(
                f"command {command_name!r} already exists in help_subcommands"
            )

        self.groups[group]["commands"][command_name] = {"description": description}
        self._group_namespace.add(command_name)

    def run(self, args=None):
        """Run the main program"""

        # Parse arguments
        parsed_args = self.parse_args(args)
        cleaned_args = {
            k: v
            for k, v in vars(parsed_args).items()
            if not k.startswith("_subcommand")
        }
        cleaned_args = argparse.Namespace(**cleaned_args)
        # TODO: hook main: self._run_main(parsed_args)  # hook to _run_main

        # Check if there is any subcommand
        if not self.subcommands:
            if self.function:
                self.function(cleaned_args)
                return
            else:
                self.print_help()
                sys.exit(1)

        # get called subcommand
        depth = 1
        subcommand = self
        while True:
            try:
                cmd_name = self._get_subcommand_name(parsed_args, depth=depth)

                if cmd_name is None:
                    subcommand.print_help()
                    sys.exit(1)
                subcommand = subcommand[cmd_name]
                depth += 1
            except AttributeError:
                break

        # If function is None, automatically it (doesn't have subparsers
        #  because we already checked errors on parse_args
        if subcommand.function is None:
            self.print_help()
            sys.exit(0)

        subcommand.function(cleaned_args)

    def register_function(self, function):
        # TODO: make function private attribute and add getter
        if self.function is not None:
            raise ValueError("function already registred")
        parameters = inspect.signature(function).parameters
        if len(parameters) != 1:
            raise ValueError(
                f"The added function {function} must have one unique parameter not {len(parameters)} parameters"
            )
        self.function = function

    # ==================== #
    # ARGPARSE WRAPPER API #
    # ==================== #

    def parse_args(self, args=None, namespace=None, remove_intern_args=None):
        if remove_intern_args is None:
            remove_intern_args = True

        self._check_errors()

        if self.autocomplete:
            argcomplete.autocomplete(self._argparse_parser)

        returned_args = self._argparse_parser.parse_args(args, namespace=namespace)
        return returned_args

    def parse_known_args(self, args=None, namespace=None):
        self._check_errors()
        returned_args = self._argparse_parser.parse_known_args(
            args, namespace=namespace
        )
        return returned_args

    # ============== #
    # DUNDER METHODS #
    # ============== #

    def __call__(self, function):
        self.register_function(function)
        return function

    def __getitem__(self, item: str):
        return self.subcommands[item]

    def __str__(self):
        return f"<SubcommandParser({self.fullname!r})>"

    def __repr__(self):
        return self.__str__()

    def iter_allcommands(self):
        """Iter all commands, self included"""
        yield self
        for parser in self.subcommands.values():
            yield from parser.iter_allcommands()

    def _check_errors(self):
        """Check if subcommands are correctly built
        This method is called before parse_args/run
        """
        for command in self.iter_allcommands():
            # If function exists it must be callable
            if command.function is not None and not callable(command.function):
                raise TypeError(f"{command.fullname}.function must be callable")

            # Todo: check that function has only one argument

            # If the command don't have any subcommand, it must have a function
            if not command.subcommands and command.function is None:
                raise ValueError(
                    f"Subcommand {command} don't have linked function or should have subpcommands"
                )

    # =============== #
    # Private methods #
    # =============== #
    def _get_subcommand_dest_name(self, depth: int = None):
        if depth is None:
            depth = self._subcommand_depth
        if depth == 1:
            return "_subcommand"
        else:
            return f"_subcommand_{depth}"

    def _get_subcommand_name(self, parsed_args, depth: int = None):
        argparse_cmd_name = self._get_subcommand_dest_name(depth)
        return getattr(parsed_args, argparse_cmd_name)

    def _print_and_exit(self, msg, status=1):
        print(msg)
        sys.exit(status)

    def _install_rich_traceback(self):
        from rich.traceback import install

        install(show_locals=True)

    def _init_argparse_subparsers(self):
        if self._argparse_subparsers is None:
            self._argparse_subparsers = self._argparse_parser.add_subparsers(
                dest=self._get_subcommand_dest_name()
            )

    def print_help(self, file=None):
        print_help(self)

    # =================== #
    # UTILS DEBUG METHODS #
    # =================== #
    def print_debug(self):
        self.positional_arguments.print()
        print()
        for key, value in self.optional_arguments_groups.items():
            print("key", key)
            value.print()
        print()
        for key, value in self.commands_groups.items():
            print("key", key)
            value.print()
