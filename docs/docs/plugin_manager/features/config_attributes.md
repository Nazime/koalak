## Customizing plugins attributes


To allow end users to easily customize your plugin, it is possible to set plugin attributes as config attribute. The PluginManager will create a configuration file with the default values, which users can modify. The new values will be loaded by default on subsequent runs.

To use this feature:

- The `PluginManager` must have the `config_path` set, either during instantiation or when the `home_path` is configured.
- Use `config_field` in your plugin class, providing a default value.
- **Initialize the Plugin Manager**: Ensure to initialize the plugin manager with `PluginManager.init()`.


```python
from koalak.plugin_manager import PluginManager, config_field


class BasePlugin:
    pass


plugins = PluginManager(
    base_plugin=BasePlugin, home_config_path="~/.myapp/plugins/plugins.toml"
)


# Creation of the plugin with config field
class AlphaPlugin(BasePlugin):
    param = config_field(50)


# Always init the plugin manager after loading of plugins
plugins.init()
```

This setup generates a default configuration in TOML format. For `AlphaPlugin`, it looks like:

```toml
[alpha]
param = 50
```

The `param` in `AlphaPlugin` is automatically set from the configuration file, or it defaults to the specified value (e.g., `50`)
