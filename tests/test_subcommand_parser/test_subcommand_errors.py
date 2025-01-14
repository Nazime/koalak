import argparse

import pytest
from koalak.subcommand_parser import SubcommandParser


def test_errors_positional_args_and_commands():
    cmd = SubcommandParser()

    cmd.add_argument("arg")  # positional argument
    with pytest.raises(ValueError):
        cmd.add_subcommand("clone")

    # Test adding subcmd then positional arg
    cmd = SubcommandParser()

    cmd.add_subcommand("clone")
    with pytest.raises(ValueError):
        cmd.add_argument("arg")  # positional argument


def test_run_attribute_not_callable():
    cmd = SubcommandParser()

    cmd_x = cmd.add_subcommand("x")
    cmd_x.function = "String and not callable"

    with pytest.raises(TypeError):
        cmd.parse_args([])


def test_subcmd_already_exists():
    main_command = SubcommandParser()

    main_command.add_subcommand("x")

    with pytest.raises(KeyError):
        main_command.add_subcommand("x")


def test_optional_arg_already_exists():
    cmd = SubcommandParser()

    cmd.add_argument("--alpha")

    with pytest.raises(argparse.ArgumentError):
        cmd.add_argument("--alpha")


# Test errors
def test_subcmdparser_without_subcommands(capsys):
    # Without subcommands should have a function or error
    main_command = SubcommandParser(description="catchme")

    with pytest.raises(ValueError):
        main_command.parse_args([])

    # if main_command have function no error is raised
    main_command.function = lambda args: print("hello")
    main_command.parse_args([])


def test_subcmdparser_subcmd_without_function():
    main_command = SubcommandParser()
    subcmd_command = main_command.add_subcommand("subcmd")

    with pytest.raises(ValueError):
        main_command.run([])


def test_run_non_existing_cmd(capsys):
    # run non-existing command print help and exit
    main_command = SubcommandParser()
    main_command.add_subcommand("mycmd").function = lambda args: print("hello")

    with pytest.raises(SystemExit):
        capsys.readouterr()  # ignore last entries
        main_command.run(["dontexist"])

    # help was printed
    assert "invalid choice" in capsys.readouterr().err.lower()
