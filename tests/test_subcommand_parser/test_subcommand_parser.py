import argparse

import coloring
import pytest
from koalak.subcommand_parser import SubcommandParser
from koalak.subcommand_parser.subcommand_parser import (
    argparse_argument_to_field_description,
)


def test_run_cmd(capsys):
    main_command = SubcommandParser()

    def run_mycmd(args):
        print(1)

    mycmd_command = main_command.add_subcommand("mycmd")
    mycmd_command.function = run_mycmd

    # assert that "mycmd" parse
    main_command.parse_args(["mycmd"])

    capsys.readouterr()  # ignore the first prints
    main_command.run(["mycmd"])
    captured = capsys.readouterr()
    assert captured.out == "1\n"


def test_run_with_args(capsys):
    main_command = SubcommandParser()

    def run_mycmd(args):
        print(args.printme)

    mycmd_command = main_command.add_subcommand("mycmd")
    mycmd_command.add_argument("printme")
    mycmd_command.function = run_mycmd

    # assert that "mycmd" parse
    main_command.parse_args(["mycmd", "1"])

    with pytest.raises(SystemExit):
        main_command.parse_args(["mycmd"])

    capsys.readouterr()  # ignore the first prints

    main_command.run(["mycmd", "test"])
    captured = capsys.readouterr()
    assert captured.out == "test\n"

    main_command.run(["mycmd", "22"])
    captured = capsys.readouterr()
    assert captured.out == "22\n"


def test_run_with_many_args(capsys):
    main_command = SubcommandParser()

    def run_mycmd(args):
        print(args.printme * args.n)

    mycmd_command = main_command.add_subcommand("mycmd")
    mycmd_command.add_argument("printme")
    mycmd_command.add_argument("-n", type=int, default=1)
    mycmd_command.function = run_mycmd

    # assert that "mycmd" parse
    main_command.parse_args(["mycmd", "1"])

    # assert that "mycmd" parse
    main_command.parse_args(["mycmd", "1", "-n", "2"])

    with pytest.raises(SystemExit):
        main_command.parse_args(["mycmd"])

    capsys.readouterr()  # ignore the first prints

    main_command.run(["mycmd", "test"])
    captured = capsys.readouterr()
    assert captured.out == "test\n"

    main_command.run(["mycmd", "hey", "-n", "3"])
    captured = capsys.readouterr()
    assert captured.out == "heyheyhey\n"


def test_nested_commands(capsys):
    main_command = SubcommandParser()

    """
    main
        - version
        - var
            - ls
            - add
    """
    version_command = main_command.add_subcommand("version")
    version_command.function = lambda args: print("version")

    var_command = main_command.add_subcommand("var")

    ls_command = var_command.add_subcommand("ls")
    ls_command.function = lambda args: print("ls")

    add_command = var_command.add_subcommand("add")
    add_command.function = lambda args: print("add")

    capsys.readouterr()  # ignore the first prints
    main_command.run(["version"])
    captured = capsys.readouterr()
    assert captured.out == "version\n"

    main_command.run(["var", "ls"])
    captured = capsys.readouterr()
    assert captured.out == "ls\n"

    main_command.run(["var", "add"])
    captured = capsys.readouterr()
    assert captured.out == "add\n"


def test_nested_commands_depth_2(capsys):
    main_command = SubcommandParser("main")

    main_command.add_subcommand("a").function = lambda args: print("d1.a")
    main_command.add_subcommand("b").function = lambda args: print("d1.b")

    depth_command = main_command.add_subcommand("depth")
    depth_command.add_subcommand("a").function = lambda args: print("d2.a")
    depth_command.add_subcommand("b").function = lambda args: print("d2.b")

    depth3_command = depth_command.add_subcommand("depth")
    depth3_command.add_subcommand("a").function = lambda args: print("d3.a")
    depth3_command.add_subcommand("b").function = lambda args: print("d3.b")

    capsys.readouterr()  # ignore the first prints
    main_command.run(["a"])
    captured = capsys.readouterr()
    assert captured.out == "d1.a\n"

    capsys.readouterr()  # ignore the first prints
    main_command.run(["b"])
    captured = capsys.readouterr()
    assert captured.out == "d1.b\n"

    with pytest.raises(SystemExit):
        main_command.run([])

    # depth2
    capsys.readouterr()  # ignore the first prints
    main_command.run(["depth", "a"])
    captured = capsys.readouterr()
    assert captured.out == "d2.a\n"

    capsys.readouterr()  # ignore the first prints
    main_command.run(["depth", "b"])
    captured = capsys.readouterr()
    assert captured.out == "d2.b\n"

    with pytest.raises(SystemExit):
        main_command.run(["depth"])

    # depth3
    capsys.readouterr()  # ignore the first prints
    main_command.run(["depth", "depth", "a"])
    captured = capsys.readouterr()
    assert captured.out == "d3.a\n"

    capsys.readouterr()  # ignore the first prints
    main_command.run(["depth", "depth", "b"])
    captured = capsys.readouterr()
    assert captured.out == "d3.b\n"

    with pytest.raises(SystemExit):
        main_command.run(["depth", "depth"])

    # None existing commands/args
    with pytest.raises(SystemExit):
        main_command.run(["a", "dontexist"])

    with pytest.raises(SystemExit):
        main_command.run(["depth", "dontexist"])

    with pytest.raises(SystemExit):
        main_command.run(["depth", "depth", "dontexist"])

    with pytest.raises(SystemExit):
        main_command.run(["a", "-x"])

    capsys.readouterr()  # to print
    # nothing in pytest


def test_nested_commands_fullname(capsys):
    main_command = SubcommandParser("main")
    assert main_command.name == "main"
    assert main_command.fullname == "main"

    a_main_command = main_command.add_subcommand("a")
    assert a_main_command.name == "a"
    assert a_main_command.fullname == "main.a"

    b_main_command = main_command.add_subcommand("b")
    assert b_main_command.name == "b"
    assert b_main_command.fullname == "main.b"

    # check that main name didn't change
    assert main_command.name == "main"
    assert main_command.fullname == "main"

    depth_command = main_command.add_subcommand("depth")
    assert depth_command.name == "depth"
    assert depth_command.fullname == "main.depth"

    main_depth_a_cmd = depth_command.add_subcommand("a")
    assert main_depth_a_cmd.name == "a"
    assert main_depth_a_cmd.fullname == "main.depth.a"

    main_depth_b_cmd = depth_command.add_subcommand("b")
    assert main_depth_b_cmd.name == "b"
    assert main_depth_b_cmd.fullname == "main.depth.b"

    main_depth_depth_cmd = depth_command.add_subcommand("depth")
    assert main_depth_depth_cmd.name == "depth"
    assert main_depth_depth_cmd.fullname == "main.depth.depth"

    main_depth_depth_a_cmd = main_depth_depth_cmd.add_subcommand("a")
    assert main_depth_depth_a_cmd.name == "a"
    assert main_depth_depth_a_cmd.fullname == "main.depth.depth.a"

    main_depth_depth_b_cmd = main_depth_depth_cmd.add_subcommand("b")
    assert main_depth_depth_b_cmd.name == "b"
    assert main_depth_depth_b_cmd.fullname == "main.depth.depth.b"


def test_help_basic(capsys):
    description = "do nothing"
    name = "maincmd"
    name_subcommand = "secondcmd"
    description_subcommand = "this is the second description"
    main_command = SubcommandParser(name, description=description)
    main_command.add_argument("--version")

    a_cmd = main_command.add_subcommand(
        name_subcommand, description=description_subcommand
    )
    capsys.readouterr()

    main_command.print_help()

    printed_help = coloring.rmgraphics(capsys.readouterr().out)
    assert description in printed_help
    assert name in printed_help
    assert name_subcommand in printed_help
    assert "--version" in printed_help


def test_help_hidden_argument(capsys):
    description = "do nothing"
    name = "maincmd"
    name_subcommand = "secondcmd"
    description_subcommand = "this is the second description"
    main_command = SubcommandParser(name, description=description)
    main_command.add_argument("--version", hide=True)

    a_cmd = main_command.add_subcommand(
        name_subcommand, description=description_subcommand
    )
    capsys.readouterr()

    main_command.print_help()

    printed_help = coloring.rmgraphics(capsys.readouterr().out)
    assert description in printed_help
    assert name in printed_help
    assert name_subcommand in printed_help
    assert "--version" not in printed_help


def test_help_hidden_command(capsys):
    description = "do nothing"
    name = "maincmd"
    name_subcommand = "secondcmd"
    description_subcommand = "this is the second description"
    main_command = SubcommandParser(name, description=description)
    main_command.add_argument("--version")

    a_cmd = main_command.add_subcommand(
        name_subcommand, description=description_subcommand, hide=True
    )
    capsys.readouterr()

    main_command.print_help()

    printed_help = coloring.rmgraphics(capsys.readouterr().out)
    assert description in printed_help
    assert name in printed_help
    assert name_subcommand not in printed_help
    assert "--version" in printed_help


def test_help_default_argument(capsys):
    description = "do nothing"
    name = "maincmd"
    name_subcommand = "secondcmd"
    description_subcommand = "this is the second description"
    default_value = "THISISADEFAULTVALUE"
    main_command = SubcommandParser(name, description=description)
    main_command.add_argument("--version", default=default_value)

    a_cmd = main_command.add_subcommand(
        name_subcommand, description=description_subcommand, hide=True
    )
    capsys.readouterr()

    main_command.print_help()

    printed_help = coloring.rmgraphics(capsys.readouterr().out)
    assert description in printed_help
    assert name in printed_help
    assert name_subcommand not in printed_help
    assert default_value in printed_help
    assert "--version" in printed_help


@pytest.mark.skip
def test_help_adding_groups(capsys):
    main_command = SubcommandParser("main")

    main_command.add_group(
        "FIRSTNAME", title="First commands", description="important commands"
    )
    main_command.add_group(
        "SECONDNAME", title="Second commands", description="useless commands"
    )

    # Third group not printed because no command is on it
    main_command.add_group(
        "THIRDNAME", title="Third commands", description="Third command description"
    )
    # 4th group not in printed because one hidden CMD on it
    main_command.add_group(
        "FOURTHNAME", title="Fourth commands", description="Fourth command description"
    )

    main_command.add_subcommand("aaa", description="do nothing", group="FIRSTNAME")
    main_command.add_subcommand("bbb", description="yes", hide=True)
    main_command.add_subcommand("ccc", description="no", group="SECONDNAME")
    main_command.add_subcommand("ddd", description="yesno", group="FIRSTNAME")

    # Third group no cmd
    # Fourth group one hidden cmd
    main_command.add_subcommand("grp4cmd1", description="yesno", group="FOURTHNAME")

    capsys.readouterr()

    main_command.print_help()

    printed_help = coloring.rmgraphics(capsys.readouterr().out)
    assert "useless commands" in printed_help
    assert "Second commands" in printed_help
    assert "First commands" in printed_help
    assert "useless commands" in printed_help
    assert "aaa" in printed_help
    assert "bbb" not in printed_help
    assert "ccc" in printed_help
    assert "ddd" in printed_help
    assert "grp4cmd1" not in printed_help

    # group name are not shown
    assert "FIRSTNAME" not in printed_help
    assert "SECONDNAME" not in printed_help
    assert "THIRDNAME" not in printed_help
    assert "FOURTHNAME" not in printed_help


def build_argparse_argument(*args, **kwargs):
    return argparse.ArgumentParser().add_argument(*args, **kwargs)


def test_add_argument_to_argument():
    argparse_arg = build_argparse_argument("arg1")
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "arg1"
    assert argument.required is True
    assert argument.name == "arg1"
    assert argument.display_name == "arg1"
    assert argument.description is None
    assert argument.type is str
    assert not argument.many

    # TODO: add more tests
    argparse_arg = build_argparse_argument("--arg2")
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "arg2"
    assert argument.required is False
    assert argument.name == "arg2"
    assert argument.display_name == "--arg2"
    assert argument.description is None
    assert argument.type is str
    assert not argument.many

    argparse_arg = build_argparse_argument("-a")
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "a"
    assert argument.required is False
    assert argument.name == "a"
    assert argument.display_name == "-a"
    assert argument.description is None
    assert argument.type is str
    assert not argument.many

    # Check type
    argparse_arg = build_argparse_argument("-a", type=int)
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "a"
    assert argument.required is False
    assert argument.name == "a"
    assert argument.display_name == "-a"
    assert argument.description is None
    assert argument.type is int
    assert not argument.many

    # Test type with stored_true/stored_false
    argparse_arg = build_argparse_argument("-a", action="store_true")
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "a"
    assert argument.required is False
    assert argument.name == "a"
    assert argument.display_name == "-a"
    assert argument.description is None
    assert argument.type is bool
    assert argument.default is False
    assert not argument.many

    argparse_arg = build_argparse_argument("-a", action="store_false")
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "a"
    assert argument.required is False
    assert argument.name == "a"
    assert argument.display_name == "-a"
    assert argument.description is None
    assert argument.type is bool
    assert argument.default is True
    assert not argument.many

    # Test default
    argparse_arg = build_argparse_argument("-a", default=5)
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "a"
    assert argument.required is False
    assert argument.name == "a"
    assert argument.display_name == "-a"
    assert argument.description is None
    assert argument.type is str
    assert argument.default == 5
    assert not argument.many

    argparse_arg = build_argparse_argument("-a")
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "a"
    assert argument.required is False
    assert argument.name == "a"
    assert argument.display_name == "-a"
    assert argument.description is None
    assert argument.type is str
    assert argument.default is None
    assert not argument.many

    argparse_arg = build_argparse_argument("test", nargs="+")
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "test"
    assert argument.required is True
    assert argument.name == "test"
    assert argument.display_name == "test"
    assert argument.description is None
    assert argument.type is str
    assert argument.default is argument.NOTHING
    assert argument.many

    argparse_arg = build_argparse_argument("test", nargs="*")
    argument = argparse_argument_to_field_description(argparse_arg)
    assert argument.dest == "test"
    assert argument.required is True
    assert argument.name == "test"
    assert argument.display_name == "test"
    assert argument.description is None
    assert argument.type is str
    assert argument.default is argument.NOTHING
    assert argument.many


# TODO: test adding function without positional arg
# TODO: remove printing from tests!
