# Quickstart

## Basics

The `plugin_manager` module enables you to create a plugin architecture where each plugin is represented by a class that inherits from a base plugin class you define. The `PluginManager` is linked to this `base_plugin` and automatically registers plugins when they inherit from it. It functions similarly to a dictionary (`dict[str, Plugin]`), with advanced features.

Key concepts:

- **Plugin Name**: Each plugin requires a `name` attribute, which acts as a unique identifier.
- **Plugin Metadata**: Plugins can have additional metadata attributes, such as description, authors, and version, to provide more context.

## Development Flow in Plugin Manager

To effectively use the `PluginManager`, follow this workflow:

1. **Define the Base Plugin**: Create a base class for your plugins, which provides utility functions and enforces constraints by requiring the implementation of specific methods or declaration of attributes in the subclasses. The base class must inherit from `koalak.plugin_manager.Plugin`.
2. **Create a PluginManager Instance**: Instantiate the `PluginManager`, passing your base class as the `base_plugin` parameter. You can also add additional configuration options to customize the behavior of the `PluginManager`.
3. **Initialize the PluginManager**: Call `PluginManager.init()` to initialize the home directory, generate a configuration file, and load plugins from the home directory.
4. **Load Plugins**: Ensure the plugin files are imported to automatically register the plugins with the `PluginManager`.
5. **Execute Business Logic**: Once plugins are registered, you can interact with them and perform the desired business logic.



## Example

In this example, we address the need for a flexible system to perform various operations on a list of integers. For instance, we might want to double each element, add the number `5` to each element, or filter the list to keep only even numbers. Additionally, these operations can be categorized: some plugins modify the size of the data (e.g., filtering out elements), while others maintain the same size (e.g., transforming values).

To handle these requirements efficiently and flexibly, we can use the `PluginManager` module. It allows us to define a standardized plugin architecture where each operation is implemented as a plugin. This approach makes it easy to extend the system by adding new operations without altering the existing code. Each plugin inherits from a base class, `ListOperation`, ensuring consistency across all plugins.


### Define the Base Plugin Class

To begin, we will create a base class `ListOperator` that serves as the parent class for all future plugins. This base class must inherit from `plugin_manager.Plugin`. We want to enforce the following constraints for all plugins:

- **Implementation of the `compute` Method**
  All plugins must implement the `compute` method, which is the core method for processing the plugin's logic. This method will act as an abstract method. Instead of raising an error during object instantiation, the error will occur at the plugin class definition if the `compute` method is not implemented. To achieve this, we decorate the method in the base class with `plugin_manager.abstract`.

- **Required `max_length` Attribute**
  Every plugin must define a required attribute `max_length` of type `int`, specifying the maximum length the plugin can handle. To enforce this constraint, we use the `plugin_manager.field` attribute and specify the type `int` through annotation.

- **Metadata: `category`**
  All plugins must include the metadata key `category`, which can either be `filter` or `transform`. To ensure this constraint is met, we define a `Metadata` class within the base class and use `plugin_manager.field` to enforce the allowed values with the `choices` parameter. It's important to note that metadata attributes are not customizable, only predefined keys, such as `category`, can be used, and we can only constrain their values.



```python
# Import everything we will need
from koalak.plugin_manager import PluginManager, Metadata, field, abstract, config_field


class ListOperation:
    class Metadata:
        # Force all plugins to have the 'category' metadata which is equal to 'filter' or 'transform'
        category = field(choices=["filter", "transform"])

    # Enforce our plugins to define the attrirbute max_length
    max_length: int = field()

    # Enforcing the implementation of `compute` method in plugins
    @abstract
    def compute(self, data: list[int]) -> list[int]:
        pass
```

### Create the PluginManager Instance

Now we need to create an instance of the `PluginManager`:

- **Optional `name`**: You can provide an optional `name` for your `PluginManager`. This is not required.
- **Link Base Plugin**: Link the base plugin to the `PluginManager` using the `base_plugin` parameter.
- **Custom Plugins via Home Path**: To allow end-users to define their own custom plugins, specify a home path. This will automatically create the directory and load any plugins found under `<plugin_home_path>/plugins`.


```python
pm_list_operations = PluginManager(
    # Optinal: give a name to our plugin manager
    "list_operations",
    # Link the BasePlugin to our plugin manager
    base_plugin=ListOperation,
    # Optional: Home path for plugins - where we can put our Custom plugins and configuration file
    home_path="~/.koalak/pm_tutorial",
)
```

### Initialize the PluginManager

After creating the `PluginManager` instance, you need to call the `PluginManager.init()` method. This will perform several important tasks, including:

- **First Run Setup**: If this is the first run of the application, it will create the home path and necessary subfolders.
- **Plugin Loading**: It will load any plugins found in `<plugin_home_path>/plugins`.
- **Configuration Loading**: If any plugins have parameters that can be customized via the `config.toml` file, it will load the appropriate configuration.

```python
pm_list_operations.init()
```

### Create our plugins

Now let's create our plugins. Our first plugin will simply multiply each element in the list by three. To register the plugin, we only need to subclass the `BasePlugin`, which will automatically register it. However, our plugin must meet all the constraints imposed by the base plugin:

- **name**: Every plugin must have a **unique** `name`. This is required by all plugin managers, even if it isn't explicitly imposed by the base plugin.
- **max_length**: We require all plugins to define the `max_length` attribute as an integer. If this attribute is missing or of an incorrect type, an error will be raised when the plugin class is defined.
- **metadata**: The base class requires all plugins to specify the `category` metadata, choosing either `transform` or `filter`. Since our plugin modifies values without changing the number of elements, we will set `category` to `transform`.

Additionally, we can provide other metadata, such as a `description`, to describe the functionality of our plugin (though this is optional).



```python
# Creating plugins by inheriting the base class
class TripleListOperator(ListOperation):
    name = "triple"
    metadata = Metadata(category="transform", description="Triple each element")
    max_length = 100

    def compute(self, data):
        return [e * 3 for e in data]
```

If we want some plugins to run before others, we can modify the `order` key in the metadata, which defaults to `50`. By setting a lower value (e.g., `1`), we can ensure that the plugin runs first.

```python
class AddFiveListOperator(ListOperation):
    name = "add_five"
    metadata = Metadata(
        category="transform",
        description="Add the number 5 to each element",
        # Ensure plugin add_five runs first (default order is 50)
        order=1,
    )
    max_length = 100

    def compute(self, data):
        return [e + 5 for e in data]
```

We can create another plugin that filters the list to keep only even numbers. This plugin will belong to the `filter` category, as it modifies the data by reducing the number of elements.

```python
class KeepEvenListOperator(ListOperation):
    name = "keep_even"
    metadata = Metadata(category="filter", description="Keep only even element")
    max_length = 100

    def compute(self, data):
        return [e for e in data if e % 2 == 0]
```

Our last plugin will add a custom number "x" to each element. By default, the value of `x` is 10. However, we want to provide the end users the ability to customize this behavior by specifying any value they want through the configuration file located at `<home_path>/config.toml`. This is accomplished using the `plugin_manager.config_field`.

```python
class AddFiveListOperator(ListOperation):
    name = "add_x"
    metadata = Metadata(
        category="transform", description="Add the number X to each element"
    )
    max_length = 100
    # This attribute "x" is a config field, meaning that it can be modified from the configuration file "~/.koalak/pm_tutorial/conf.toml"
    x = config_field(10)

    def compute(self, data):
        return [e + self.x for e in data]
```

### Implement Core Business Logic

Now that we have defined all our plugins, we can implement the core logic of the app. To interact with a plugin, we can either:

- Retrieve a specific plugin by its unique name using `plugin_manager[plugin_name]`.
- Iterate through all the plugins in the `plugin_manager`, which will be returned sorted by `metadata.order`.

Here's how to do it:



```python
data = [1, 2, 3, 4, 5]
print(f"Initial data {data}\n")

# Iterating through all plugins
# The plugin with the lowest metadata.order will run first.
for plugin_cls in pm_list_operations:
    plugin_instance = plugin_cls()
    print(
        f"Running plugin '{plugin_cls.name}' of category '{plugin_cls.metadata.category}'"
    )
    data = plugin_instance.compute(data)
    print(f"Current data {data}")
print()

# Get plugin by name
plugin_cls = pm_list_operations["add_five"]
plugin_instance = plugin_cls()
data = plugin_instance.compute(data)
print(f"After running 'add_five' plugin again: {data}")
```

### All the code

```python
# Importing PluginManager
from koalak.plugin_manager import (
    PluginManager,
    Plugin,
    Metadata,
    field,
    abstract,
    config_field,
)


# ================================= #
# 01 - Define the Base Plugin class #
# ================================= #
class ListOperation(Plugin):
    class Metadata:
        # Force all plugins to have the 'category' metadata which is equal to 'filter' or 'transform'
        category = field(choices=["filter", "transform"])

    # Enforcing the implementation of `compute` method in plugins
    @abstract
    def compute(self, data: list[int]) -> list[int]:
        pass


# ================================== #
# 02 - Create PluginManager Instance #
# ================================== #

pm_list_operations = PluginManager(
    # Optinal: give a name to our plugin manager
    "list_operations",
    # Link the BasePlugin to our plugin manager
    base_plugin=ListOperation,
    # Optional: Home path for plugins - where we can put our Custom plugins and configuration file
    home_path="~/.koalak/pm_tutorial",
)

# =============================#
# 03 - Init the plugin manager #
# ============================ #
pm_list_operations.init()

# ======================= #
# 04 - Create the plugins #
# ======================= #

# Creating plugins by inheriting the base class
class TripleListOperator(ListOperation):
    name = "triple"
    metadata = Metadata(category="transform", description="Triple each element")
    max_length = 100

    def compute(self, data):
        return [e * 3 for e in data]


class AddFiveListOperator(ListOperation):
    name = "add_five"
    metadata = Metadata(
        category="transform",
        description="Add the number 5 to each element",
        # Ensure plugin add_five run first. By default order is equal to 50.
        order=1,
    )
    max_length = 100

    def compute(self, data):
        return [e + 5 for e in data]


class KeepEvenListOperator(ListOperation):
    name = "keep_even"
    metadata = Metadata(category="filter", description="Keep only even element")
    max_length = 100

    def compute(self, data):
        return [e for e in data if e % 2 == 0]


class AddFiveListOperator(ListOperation):
    name = "add_x"
    metadata = Metadata(
        category="transform", description="Add the number X to each element"
    )
    max_length = 100
    # This attribute "x" is a config field, meaning that it can be modified from the configuration file "~/.koalak/pm_tutorial/conf.toml"
    x = config_field(10)

    def compute(self, data):
        return [e + self.x for e in data]


# ================================== #
# 05 - Implement core business logic #
# ================================== #

data = [1, 2, 3, 4, 5]
print(f"Initial data {data}\n")

# Iterating through all plugins
# The plugin add_five will be returned first, since it has the lower metadata.order.
for plugin_cls in pm_list_operations:
    plugin_instance = plugin_cls()
    print(
        f"Running plugin '{plugin_cls.name}' of category '{plugin_cls.metadata.category}'"
    )
    data = plugin_instance.compute(data)
    print(f"Current data {data}")
print()

# Get plugin by name
plugin_cls = pm_list_operations["add_five"]
plugin_instance = plugin_cls()
data = plugin_instance.compute(data)
print(f"After running 'add_five' plugin again: {data}")
```

If you run the script, the configuration file "~/.koalak/pm_tutorial/conf.toml" is created, you can modify it's value and run the script again to obtain different results.
