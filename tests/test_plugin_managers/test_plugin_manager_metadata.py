import pytest
from koalak.plugin_manager import Metadata, Plugin, PluginManager, abstract, field


def test_metadata_working_normally():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "A"
        metadata = Metadata(description="A plugin")

    assert APlugin.metadata.description == "A plugin"


def test_metadata_default_values():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "A"

    assert APlugin.metadata.description is None
    assert APlugin.metadata.authors == []
    assert APlugin.metadata.version == "0.0.1"
    assert APlugin.metadata.order == 50


def test_metadata_errors_type_of_field():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    with pytest.raises(TypeError):

        class BPlugin(BasePlugin):
            name = "B"
            # Description present but int and not str
            metadata = Metadata(description=12)


def test_metadata_errors_metadata_function_with_unexpected_argument():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    with pytest.raises(TypeError):

        class BPlugin(BasePlugin):
            name = "B"
            # Description present but int and not str
            metadata = Metadata(y=12)


def test_metadata_errors_metadata_created_with_function_not_dict():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    with pytest.raises(TypeError):

        class BPlugin(BasePlugin):
            name = "B"
            metadata = {"description": "B Plugin"}


def test_metadata_order_iter():
    class BasePlugin(Plugin):
        pass

    plugins = PluginManager(base_plugin=BasePlugin)

    class A(BasePlugin):
        name = "A"
        metadata = Metadata(order=80)

    class B(BasePlugin):
        name = "B"
        metadata = Metadata(order=20)

    class C(BasePlugin):
        name = "C"
        metadata = Metadata(order=90)

    assert list(plugins) == [B, A, C]


def test_metadata_required_attributes_is_present_with_choices():
    class BasePlugin(Plugin):
        class Metadata:
            category = field(choices=["alpha", "beta"])

    plugins = PluginManager(base_plugin=BasePlugin)

    class A(BasePlugin):
        name = "A"
        metadata = Metadata(category="alpha")

    with pytest.raises(ValueError):

        class B(BasePlugin):
            name = "B"
            metadata = Metadata(description="I dont have a category")

    with pytest.raises(ValueError):

        class C(BasePlugin):
            name = "C"
            metadata = Metadata(category="wrong", description="I have bad category")
