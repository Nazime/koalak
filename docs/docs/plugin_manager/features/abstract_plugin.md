# Abstract Plugin

You can create an abstract plugin to group common methods and attributes for specific plugins:

- The PluginManager will not enforce constraints on an abstract plugin.
- The PluginManager will not register the abstract plugin itself.

To define an abstract plugin, set the `abstract = True` attribute in the class. The `PluginManager` will recognize this on the abstract class but will not apply it to its subclasses.

```python
# This is an abstract plugin
class AbstractPlugin(BasePlugin):
    abstract = True

    def util_method(self):
        pass


# This is a concrete plugin, not abstract
class AlphaPlugin(AbstractPlugin):
    name = "alpha"

    def do_run(self):
        x = self.util_method()
        ...
```
