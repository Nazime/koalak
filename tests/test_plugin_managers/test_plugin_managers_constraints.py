from typing import List

import pytest
from koalak.plugin_manager import Plugin, PluginManager, abstract, field

from tests.test_plugin_managers.utils import get_unique_name


def test_constraint_field_not_present():
    """Test that attribute "help" is required"""

    class BasePlugin(Plugin):
        help = field()  # help attribute is required

    plugins = PluginManager(base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = get_unique_name()
        help = "Something"

    class BPlugin(BasePlugin):
        name = get_unique_name()
        help = 12  # can be of any type

    with pytest.raises(AttributeError):
        # Must define help
        class CPlugin(BasePlugin):
            name = get_unique_name()


def test_constraint_field_with_its_type_through_argument():
    class BasePlugin(Plugin):
        help = field(type=str)

    plugins = PluginManager(base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "A"
        help = "Something"

    with pytest.raises(TypeError):
        # Help must be a string
        class BPlugin(BasePlugin):
            name = "B"
            help = 5


def test_constraint_field_with_its_type_through_annotation():
    class BasePlugin(Plugin):
        help: str = field()

    plugins = PluginManager(base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "A"
        help = "Something"

    with pytest.raises(TypeError):
        # Help must be a string
        class BPlugin(BasePlugin):
            name = "B"
            help = 5


def test_constraint_field_with_list_annotation():
    class BasePlugin(Plugin):
        help: List[str] = field()

    plugins = PluginManager(base_plugin=BasePlugin)

    class P(BasePlugin):
        name = get_unique_name()
        help = ["Something"]

    class P(BasePlugin):
        name = get_unique_name()
        help = []

    with pytest.raises(TypeError):
        # Help must be a string
        class P(BasePlugin):
            name = get_unique_name()
            help = 5

    with pytest.raises(TypeError):
        # Help must be a string
        class P(BasePlugin):
            name = get_unique_name()
            help = "test"

    with pytest.raises(TypeError):
        # Help must be a string
        class P(BasePlugin):
            name = get_unique_name()
            help = [1]

    with pytest.raises(TypeError):
        # Help must be a string
        class P(BasePlugin):
            name = get_unique_name()
            help = ["lol", 1]


def test_constraint_attr_choices():
    class BasePlugin(Plugin):
        help = field(type=int, choices=[1, 2])

    plugins = PluginManager(base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "A"
        help = 1

    with pytest.raises(ValueError):
        # Help must be 1 or 2
        class BPlugin(BasePlugin):
            name = "B"
            help = 3


def test_constraint_attr_min_max():
    class BasePlugin(Plugin):
        help = field(type=int, min=1, max=5)

    plugins = PluginManager(base_plugin=BasePlugin)

    class APlugin(BasePlugin):
        name = "A"
        help = 3  # Valid: within the range [1, 5]

    class BPlugin(BasePlugin):
        name = "B"
        help = 5  # Valid: within the range [1, 5]

    with pytest.raises(ValueError):
        # Help must be >= 1
        class CPlugin(BasePlugin):
            name = "C"
            help = -1  # Invalid: below the minimum value

    with pytest.raises(ValueError):
        # Help must be <= 5
        class DPlugin(BasePlugin):
            name = "D"
            help = 6  # Invalid: above the maximum value


def test_constraints_simple_abstract_method():
    class BasePlugin(Plugin):
        @abstract
        def x(self):
            pass

    plugins = PluginManager(base_plugin=BasePlugin)

    class XTest(BasePlugin):
        name = "x"

        def x(self):
            pass

    with pytest.raises(AttributeError):

        class YTest(BasePlugin):
            name = "y"
