# Plugins Constraints

Plugin constraints are checks performed when a plugin is loaded (at class creation), allowing you to detect potential issues early, before instantiation. These constraints ensure that subclasses meet certain requirements, such as implementing specific methods or having necessary attributes.

You can enforce the following constraints on your plugins:

- **Abstract Method**: Forces plugins to implement a specific method.
    - Use the `koalak.plugin_manager.abstract` decorator.

- **Force Attribute**: Ensures plugins have specific attributes, with constraints on their types and values.
    - **Type**: Enforce the attribute to be of a particular type.
    - **Min/Max**: Set minimum and maximum values.
    - **Choices**: Limit the attribute to specific values.

```python
from koalak.plugin_manager import field, abstract


class BasePlugin:
    # Force subclass to define a class attribute 'extension'
    extension = field()

    # Force the subclass to define a class attribute 'speed' of type 'int'
    speed: int = field()

    # Force the attribute to have a value from a list of possibilities
    os = field(choices=["linux", "windows"])

    # Adding an abstract method without checking the signature
    @abstract
    def do_run(self):
        pass
```
