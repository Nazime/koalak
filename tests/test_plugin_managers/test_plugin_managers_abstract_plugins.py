import pytest
from koalak.plugin_manager import Plugin, PluginManager, abstract, field


def test_simple_abstract_subplugin():
    class BasePlugin(Plugin):
        # This plugin requires the description attribute
        description: str = field()

    plugins = PluginManager(base_plugin=BasePlugin)

    # Plugin A must have the attribute "name"
    with pytest.raises(AttributeError):

        class APlugin(BasePlugin):
            name = "A"

    # Abstract class are not checked!
    class AbstractPlugin(BasePlugin):
        abstract = True


def test_abstract_subcplugin_with_other_fields():
    class BasePlugin(Plugin):
        # This plugin requires the description attribute
        description: str = field()

    plugins = PluginManager(base_plugin=BasePlugin)

    # Plugin A must have the attribute "name"
    with pytest.raises(AttributeError):

        class APlugin(BasePlugin):
            name = "A"

    # Abstract class are not checked!
    class AbstractPlugin(BasePlugin):
        abstract = True
        help: str = field()

    # Plugin must have help and description
    with pytest.raises(AttributeError):

        class BPlugin(AbstractPlugin):
            name = "B"
            help = "test"

    with pytest.raises(AttributeError):

        class CPlugin(AbstractPlugin):
            name = "C"
            description = "test"


def test_abstract_subcplugin_overwirting_field():
    class BasePlugin(Plugin):
        # This plugin requires the description attribute
        description: str = field()

    plugins = PluginManager(base_plugin=BasePlugin)

    # Plugin A must have the attribute "name"
    with pytest.raises(TypeError):

        class APlugin(BasePlugin):
            name = "A"
            description = 1  # description must be int

    # Abstract class are not checked!
    class AbstractPlugin(BasePlugin):
        abstract = True
        description: int = field()

    class BPlugin(AbstractPlugin):
        name = "B"
        description = 1  # now description can be int
