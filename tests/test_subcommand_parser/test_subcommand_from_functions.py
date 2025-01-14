import pytest
from koalak.subcommand_parser import SubcommandParser


def test_from_function_simple(capsys):
    def greet():
        print("Hello")

    cmd = SubcommandParser.from_function(greet)
    cmd.run([])
    assert capsys.readouterr().out == "Hello\n"


def test_from_function_main_cmd_2_builtin_types_optionals(capsys):
    def greet(greet: str = "Hello", repeat: int = 1):
        for i in range(repeat):
            print(greet)

    cmd = SubcommandParser.from_function(greet)

    cmd.run([])
    assert capsys.readouterr().out == "Hello\n"

    cmd.run(["--greet", "plop"])
    assert capsys.readouterr().out == "plop\n"
    cmd.run(["--greet", "plop", "--repeat", "2"])
    assert capsys.readouterr().out == "plop\nplop\n"


def test_from_function_main_cmd_2_builtin_optional_and_positional(capsys):
    def greet(greet: str, *, repeat: int = 1):
        for i in range(repeat):
            print(greet)

    cmd = SubcommandParser.from_function(greet)

    cmd.run(["plop"])
    assert capsys.readouterr().out == "plop\n"
    cmd.run(["plop", "--repeat", "2"])
    assert capsys.readouterr().out == "plop\nplop\n"


def test_from_function_with_instance(capsys):
    class A:
        def __init__(self, name):
            self.name = name

        def greet(self, greet: str, *, repeat: int = 1):
            for i in range(repeat):
                print(self.name, greet)

    a = A("xxx")
    cmd = SubcommandParser.from_function(A.greet, default_instance=a)

    cmd.run(["plop"])
    assert capsys.readouterr().out == "xxx plop\n"
    cmd.run(["plop", "--repeat", "2"])
    assert capsys.readouterr().out == "xxx plop\nxxx plop\n"


def test_add_cmd_from_function_main_cmd_2_builtin_optional_and_positional(capsys):
    def greet(greeting: str, *, repeat: int = 1):
        for i in range(repeat):
            print(greeting)

    cmd = SubcommandParser()
    cmd_greet = cmd.add_subcommand_from_function(greet)

    assert len(cmd.subcommands) == 1
    assert cmd.subcommands["greet"] is cmd_greet

    assert len(cmd_greet.positional_arguments) == 1
    assert cmd_greet.positional_arguments["greeting"].type is str

    assert len(cmd_greet.optional_arguments) == 1
    assert cmd_greet.optional_arguments["repeat"].type is int
    assert cmd_greet.optional_arguments["repeat"].default == 1

    cmd.run(["greet", "plop"])
    assert capsys.readouterr().out == "plop\n"
    cmd.run(["greet", "plop", "--repeat", "2"])
    assert capsys.readouterr().out == "plop\nplop\n"
