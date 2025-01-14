from typing import TYPE_CHECKING

from .consts import KEY_PLUGIN_MANAGER

if TYPE_CHECKING:
    from .plugin_manager import PluginManager
    from .plugin_metadata import Metadata


class Plugin:
    """Base class for all BasePlugins and Plugins"""

    name: str
    metadata: "Metadata"

    def __init_subclass__(cls, **kwargs):
        """Method to validate plugins"""
        # In order to not check base_plugin, we put the plugin_manager
        #  in a special attribute name after init base_plugin, so we checks
        #  only subclasses
        if not hasattr(cls, KEY_PLUGIN_MANAGER):
            return

        plugin_manager: PluginManager = getattr(cls, KEY_PLUGIN_MANAGER)
        # Automatically register subclasses only if 'auto_register' is True
        if plugin_manager.auto_register:
            plugin_manager.register(cls)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.metadata.base_plugin.__name__}('{self.name}')>"
