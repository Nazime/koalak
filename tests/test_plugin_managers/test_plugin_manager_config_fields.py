import pytest
from koalak.plugin_manager import Plugin, PluginManager, abstract, config_field, field


def test_plugin_manager_simple_config(tmp_path):
    config_path = tmp_path / "config.toml"

    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(home_config_path=config_path, base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "alpha"
        param = config_field(50)

    # The default value must be correctly set before the init
    assert APlugin.param == 50

    plugins.init()

    assert APlugin.param == 50
    assert plugins.config["alpha"]["param"] == 50


def test_plugin_manager_existing_config(tmp_path):
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """[alpha]
param=100
"""
        )

    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(home_config_path=config_path, base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "alpha"
        param = config_field(50)

    # The default value must be correctly set before the init
    assert APlugin.param == 100

    plugins.init()

    assert APlugin.param == 100
    assert plugins.config["alpha"]["param"] == 100


def test_plugin_manager_2_fields_one_exising_one_not(tmp_path):
    config_path = tmp_path / "config.toml"
    with open(config_path, "w") as f:
        f.write(
            """[alpha]
param=100
"""
        )

    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(home_config_path=config_path, base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "alpha"
        param = config_field(50)
        param2 = config_field("fast")

    # The default value must be correctly set before the init
    assert APlugin.param == 100
    assert APlugin.param2 == "fast"

    plugins.init()

    assert APlugin.param == 100
    assert plugins.config["alpha"]["param"] == 100
    assert plugins.config["alpha"]["param2"] == "fast"


def test_plugin_manager_no_config_path_error(tmp_path):
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    # if no config file, raise error when using config_field
    with pytest.raises(ValueError):

        class APlugin(BasePlugin):
            name = "alpha"
            param = config_field(50)
