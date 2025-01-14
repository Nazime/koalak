# Metadata

Each plugin can have custom metadata through the `metadata` attribute, using the `koalak.plugin_manager.Metadata` class. If no metadata is specified, a default instance with empty values is automatically created for the plugin. In addition, the `name` attribute is required for all plugins, acting as a unique identifier.

## List of Metadata

All plugins include the following metadata:

Basic metadata

- **description**: `str` - A description of the plugin, defaulting to `None`.
- **authors**: `list[str]` - A list of authors of the plugin.
- **version**: `str` - The version of the plugin, defaulting to `"0.0.1"`.

Search and Filter Metadata

- **category**: `str` - The category of the plugin, defaulting to `None`. A plugin can have only one category.
- **sub_category**: `str` - The sub-category of the plugin, defaulting to `None`. A plugin can have only one sub-category.
- **tags**: `str | list[str]` - Tags for the plugin, defaulting to `None`. A plugin can have multiple tags.

Metadata used by the plugin manager

- **order**: `int | float` - The order in which the plugin will be processed, defaulting to `50`. Plugins with a lower `order` will be processed first.
- **dependencies**: `list[str]` - A list of Python library dependencies for the plugin, defaulting to an empty list. The plugin manager can check if all dependencies are met.
- **exe_dependencies**: `list[str]` - A list of executable dependencies required by the plugin in the system's `PATH`, defaulting to an empty list. The plugin manager can check if all dependencies are met.

## Control Sequence of Plugins (with metadata.order)

To control the sequence in which plugins are processed, you can define the `order` metadata for each plugin. The `order` attribute allows you to specify the relative order of plugins when iterating through them. By default, plugins with no specified `order` will be assigned a value of `50`.

```python
# -- begining of boiler plate ---
from koalak.plugin_manager import PluginManager, Metadata


class BasePlugin:
    pass


pm = PluginManager(base_plugin=BasePlugin)
# -- end of boiler plate --


class AlphaPlugin(BasePlugin):
    name = "alpha"
    metadata = Metadata(order=60)  # Order set to 60


class BetaPlugin(BasePlugin):
    name = "beta"
    # No order specified, defaults to 50


class OmegaPlugin(BasePlugin):
    name = "omega"
    metadata = Metadata(order=20)  # Order set to 20


# Plugins will be processed in the order: OmegaPlugin, BetaPlugin, AlphaPlugin
assert list(pm) == [OmegaPlugin, BetaPlugin, AlphaPlugin]
```

## Filtering plugins with tags and categories

You can easily filter plugins based on their `category`, `sub_catgory` and `tags` metadata. This allows you to organize plugins into groups or apply custom filtering logic to select relevant plugins for specific tasks.

```python
# -- begining of boiler plate --
from koalak.plugin_manager import PluginManager, Metadata


class BasePlugin:
    pass


pm = PluginManager(base_plugin=BasePlugin)
# -- end of boiler plate --


class AlphaPlugin(BasePlugin):
    name = "alpha"
    metadata = Metadata(category="linux", tags=["update"])


class BetaPlugin(BasePlugin):
    name = "beta"
    metadata = Metadata(category="linux", tags=["users"])


class OmegaPlugin(BasePlugin):
    name = "omega"
    metadata = Metadata(category="windows", tags=["users"])


# Filtering by category "linux"
assert list(pm(category="linux")) == [AlphaPlugin, BetaPlugin]

# Filtering by tag "users"
assert list(pm(tags="users")) == [BetaPlugin, OmegaPlugin]
```
