from koalak.subcommand_parser import SubcommandParser


def test_optional_arguments_structure_name_and_display_name():
    cmd = SubcommandParser()
    cmd.add_argument("--test")
    arg = cmd.optional_arguments["test"]
    assert arg.name == "test"
    assert arg.display_name == "--test"

    cmd = SubcommandParser()
    cmd.add_argument("-t")
    arg = cmd.optional_arguments["t"]
    assert arg.name == "t"
    assert arg.display_name == "-t"

    cmd = SubcommandParser()
    cmd.add_argument("-t", "--test")
    arg = cmd.optional_arguments["test"]
    assert arg.name == "test"
    assert arg.display_name == "-t --test"


def test_positional_and_optional_arguments_structure():
    cmd = SubcommandParser()
    assert list(cmd.positional_arguments) == []
    assert list(cmd.optional_arguments) == []

    cmd.add_argument("test")
    assert list(cmd.optional_arguments) == []
    assert len(cmd.positional_arguments) == 1

    arg = cmd.positional_arguments["test"]
    assert arg.name == "test"
    assert arg.dest == "test"
    assert arg.required is True
    assert arg.type is str

    # adding second arg
    cmd.add_argument("test2")
    assert list(cmd.optional_arguments) == []
    assert len(cmd.positional_arguments) == 2

    arg = cmd.positional_arguments["test"]
    assert arg.name == "test"
    assert arg.dest == "test"
    assert arg.required is True
    assert arg.type is str

    arg = cmd.positional_arguments["test2"]
    assert arg.name == "test2"
    assert arg.dest == "test2"
    assert arg.required is True
    assert arg.type is str

    # Adding optional arg
    cmd.add_argument("--test3", type=int)
    assert len(cmd.optional_arguments) == 1
    assert len(cmd.positional_arguments) == 2

    arg = cmd.positional_arguments["test"]
    assert arg.name == "test"
    assert arg.dest == "test"
    assert arg.required is True
    assert arg.type is str

    arg = cmd.positional_arguments["test2"]
    assert arg.name == "test2"
    assert arg.dest == "test2"
    assert arg.required is True
    assert arg.type is str

    arg = cmd.optional_arguments["test3"]
    assert arg.name == "test3"
    assert arg.dest == "test3"
    assert arg.required is False
    assert arg.type is int
