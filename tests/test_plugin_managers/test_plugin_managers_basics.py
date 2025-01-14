import pytest
from koalak.plugin_manager import Plugin, PluginManager, abstract, field

from .utils import get_unique_base_plugin


def test_api_working():
    # Unnamed PluginManager works
    PluginManager(base_plugin=get_unique_base_plugin())

    # Named PluginManager works
    PluginManager("_koalak_unittest", base_plugin=get_unique_base_plugin())


def test_unnamed_plugin_manager_without_framework():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    class SimplePlugin(BasePlugin):
        name = "simple"

    assert plugins["simple"] is SimplePlugin
    assert "simple" in plugins
    assert SimplePlugin in plugins
    assert list(plugins) == [SimplePlugin]
    assert len(plugins) == 1


def test_named_plugin_manager_without_framework():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager("plugin", base_plugin=BasePlugin)

    class SimplePlugin(BasePlugin):
        name = "simple"

    assert plugins["simple"] == SimplePlugin
    assert "simple" in plugins
    assert SimplePlugin in plugins
    assert list(plugins) == [SimplePlugin]


def test_register_base_plugin():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager("plugin", base_plugin=BasePlugin)

    class SimplePlugin(BasePlugin):
        name = "simple"

    assert plugins["simple"] == SimplePlugin
    assert "simple" in plugins
    assert SimplePlugin in plugins
    assert list(plugins) == [SimplePlugin]


def test_two_plugins_without_framework():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager("plugin", base_plugin=BasePlugin)

    class OnePlugin(BasePlugin):
        name = "one"

    class TwoPlugin(BasePlugin):
        name = "two"

    assert plugins["one"] == OnePlugin
    assert "one" in plugins
    assert OnePlugin in plugins

    assert plugins["two"] == TwoPlugin
    assert "two" in plugins
    assert TwoPlugin in plugins

    assert list(plugins) == [OnePlugin, TwoPlugin]
    assert len(plugins) == 2


def test_name_is_required():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    class Alpha(BasePlugin):
        name = "alpha"

    with pytest.raises(AttributeError):

        class Beta(BasePlugin):
            # This plugin dont have attribute 'name'
            pass


def test_name_is_unique():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    class Alpha(BasePlugin):
        name = "alpha"

    with pytest.raises(ValueError):

        class Alpha(BasePlugin):
            name = "alpha"


def test_name_is_str():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    with pytest.raises(ValueError):

        class Alpha(BasePlugin):
            name = 5


# =============== #
# UTILS FONCTIONS #
# =============== #
def test__repr__and__str__():
    plugins = PluginManager(base_plugin=get_unique_base_plugin())
    assert repr(plugins) == str(plugins) == "<PluginManager>"

    plugins = PluginManager("tools", base_plugin=get_unique_base_plugin())
    assert repr(plugins) == str(plugins) == "<PluginManager [tools]>"
