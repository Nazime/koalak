import glob
import inspect
import os
from importlib.metadata import entry_points
from pathlib import Path
from typing import Dict, Generic, Iterable, List, Type, TypeVar, Union

from koalak.config import Config
from koalak.containers import Container, search

from ..descriptions.field_description import FieldDescription
from .base_plugin import Plugin
from .constraints import AbstractMethodConstraint, AttributeConstraint, BaseConstraint
from .consts import (
    KEY_ABSTRACT_METHOD,
    KEY_ATTRIBUTES_CONSTRAINTS,
    KEY_METADATA_CONSTRAINTS,
    KEY_PLUGIN_MANAGER,
)
from .plugin_metadata import METADATA_ATTRIBUTES_NAMES, Metadata

# TODO: delete koalak_object_stroage
# TODO: Remove things


T = TypeVar("T", bound=Plugin)
G = TypeVar("G")


class ConfigDescription(FieldDescription):
    pass


def config_field(
    default: G = None,
    *,
    name: str = None,
) -> G:
    return ConfigDescription(name=name, default=default)


def normalize_to_path_or_none(value) -> Union[None, Path]:
    if value is None:
        return None
    if isinstance(value, Path):
        return value.expanduser()
    elif isinstance(value, str):
        return Path(value).expanduser()
    else:
        raise TypeError("Must be Path or str")


class PluginManager(Generic[T]):
    """
    Container for plugins (add, request, specify plugins).

    This is the most important feature of koalak.

    """

    def __init__(
        self,
        name: str = None,
        *,
        description: str = None,
        base_plugin: Type[T],
        auto_register: bool = None,
        auto_check: bool = None,
        entry_point: str = None,
        # Paths
        builtin_data_path: Union[str, Path] = None,
        builtin_plugins_path: Union[str, Path] = None,
        home_path: Union[str, Path] = None,
        home_config_path: Union[str, Path] = None,
        home_data_path: Union[str, Path] = None,
        home_plugins_path: Union[str, Path] = None,
        exceptions_path: Union[str, Path] = None,
    ):
        """

        Args:
            name: name of the plugin manager (can be None)
            auto_register: if True, automatically register plugins when subclassing baseplugin
            auto_check: if True, automatically check if plugins are well constructed
            home_path: path for plugin manager, to load home plugins

        """

        # TODO: add option to disable loading from homepath

        if auto_register is None:
            auto_register = True

        if auto_check is None:
            auto_check = True

        home_path = normalize_to_path_or_none(home_path)
        builtin_data_path = normalize_to_path_or_none(builtin_data_path)
        builtin_plugins_path = normalize_to_path_or_none(builtin_plugins_path)
        home_config_path = normalize_to_path_or_none(home_config_path)
        home_data_path = normalize_to_path_or_none(home_data_path)
        home_plugins_path = normalize_to_path_or_none(home_plugins_path)

        if home_path is not None:
            if home_config_path is None:
                home_config_path = home_path / "config.toml"
            if home_data_path is None:
                home_data_path = home_path / "data"
            if home_plugins_path is None:
                home_plugins_path = home_path / "plugins"
            if exceptions_path is None:
                home_path / "exceptions"

        self.name: str = name
        self.description: str = description
        self.entry_point = entry_point
        self.builtin_data_path = builtin_data_path
        self.builtin_plugins_path = builtin_plugins_path
        self.home_path: Path = home_path
        self.config_path: Path = home_config_path
        self.home_data_path: Path = home_data_path
        self.home_plugins_path: Path = home_plugins_path
        self.exceptions_path: Path = exceptions_path

        if self.config_path is not None:
            config = Config(self.config_path)
        else:
            config = None
        self.config = config
        self.auto_register: bool = auto_register  # TODO: implement then test me
        self.auto_check: bool = auto_check  # TODO implement me / test me
        self._plugins: dict[str, Type[T]] = {}
        self._initialized: bool = False
        self._config_dict_form_plugins = {}

        self._base_plugin: Type[T] = base_plugin
        self._register_base_plugin(base_plugin)

    # ========== #
    # PROPERTIES #
    # ========== #
    @property
    def base_plugin(self):
        return self._base_plugin

    # ========== #
    # Public API #
    # ========== #
    def register(self, plugin_cls: Type[T], check: bool = None):
        """
        Register the plugin and check if it's correctly implemented

        Args:
            plugin_cls: plugin to register
            check: if True check if plugin respect all constraints (default taken from self.autocheck)
        """

        if check is None:
            check = self.auto_check

        # If not abstract register

        is_cls_abstract = plugin_cls.__dict__.get("abstract", False)
        if not is_cls_abstract:
            # -- Check name attribute -- #
            if not hasattr(plugin_cls, "name"):
                raise AttributeError(f"name is required for plugins '{plugin_cls}'")

            name = plugin_cls.name
            if name in self._plugins:
                raise ValueError(f"plugin '{name}' already exist")

            if not isinstance(name, str):
                raise ValueError(f"plugin name {name!r} must be a string")

            # -- Check metadata -- #
            if not hasattr(plugin_cls, "metadata"):
                plugin_cls.metadata = Metadata()

            if not isinstance(plugin_cls.metadata, Metadata):
                raise TypeError(
                    f"plugin metadata for '{name}' must be of type Metadata"
                )

            # Check constraint before registring
            if check:
                self.check(plugin_cls)

            # TODO: read again config fields
            self._check_config_fields(plugin_cls)
            # FIXME: Remove or document __init_plugin__

            plugin_cls.metadata.plugin_manager = self
            self._plugins[name] = plugin_cls
        else:
            # If it's an abstract class (with abstract = True)
            #   add all the contraints to the __koalak__.constraints dict and remove the field attributes
            self._add_constraints_to_cls(plugin_cls)

    def check(self, plugin):
        """Check if plugin respect all constraints"""
        for constraint in self._iter_constraints(plugin):
            constraint.check(plugin)

    def instances(self, *args, **kwargs):
        """Return instances of each plugin after instantiations with args/kwargs"""
        for plugin_cls in self:
            yield plugin_cls(*args, **kwargs)

    def init(self, _homepath_initialized: set = None):
        # TODO: read me again
        _homepath_initialized = _homepath_initialized or set()

        if self._initialized:
            raise TypeError("Plugin Already initiated")
        self._initialized = True

        # FIXME: this condition must be checked with framework,
        #  otherwise no init will happen for config
        if self.home_path in _homepath_initialized:
            return
        self._init_home()
        self._load_plugins()
        self._init_config()

        # TODO: document & test entry points
        # Load plugins from other libraries entry points
        if self.entry_point:
            for entry_point in entry_points(group=self.entry_point, name=self.name):
                try:
                    entry_point.load()
                except ModuleNotFoundError as e:
                    package_distribution = entry_point.dist.name
                    raise ModuleNotFoundError(
                        f"Failed to load entry point '{entry_point.name}' from distribution '{package_distribution}'. "
                        f"Ensure the package is installed and accessible. Missing module: '{entry_point.value}'"
                    ) from e

    def iter(
        self,
        *,
        name: str | list[str] = None,
        category: str | list[str] = None,
        sub_category: str | list[str] = None,
        tags: str | list[str] = None,
        authors: str | list[str] = None,
    ):

        if isinstance(name, str):
            name = [name]
        if name is not None:
            for e in name:
                if e not in self:
                    raise ValueError(f"Plugin '{e}' not registred")

        # Filter with metadata
        iterable = search(
            self,
            key=lambda x, e: getattr(x.metadata, e),
            category=category,
            sub_category=sub_category,
            tags=tags,
            authors=authors,
        )
        iterable = Container(iterable).filter(name=name)
        yield from iterable

    def get_home_data_path(self, *paths):
        return self.home_data_path.joinpath(*paths)

    def get_builtin_data_path(self, *paths):
        return self.builtin_data_path.joinpath(*paths)

    def get_exceptions_path_for_plugin(self, plugin_name: str):
        return self.home_path / "exceptions" / f"{plugin_name}.exceptions.txt"

    # ============== #
    # DUNDER METHODS #
    # ============== #
    def __contains__(self, item: str | T):
        """If plugin or name of plugin is contained, return True"""
        if isinstance(item, type) and issubclass(item, self._base_plugin):
            # TODO: check how to handle annotation for baseplugin
            #  have some super baseplugin for all base plugins?
            item = item.name

        if not isinstance(item, str):
            raise ValueError("itme must be of type str or base_plugin")
        return item in self._plugins

    def __getitem__(self, item: str) -> Type[T]:
        if isinstance(item, type) and issubclass(item, self._base_plugin):
            item = item.name

        return self._plugins.__getitem__(item)

    def __iter__(self) -> Iterable[Type[T]]:
        yield from sorted(self._plugins.values(), key=lambda e: e.metadata.order)

    def __len__(self):
        """Return number of plugins (without abstract plugins)"""
        return len(self._plugins)

    def __bool__(self):
        return bool(self._plugins)

    def __repr__(self):
        if self.name:
            return f"<PluginManager [{self.name}]>"
        else:
            return f"<PluginManager>"

    def __str__(self):
        return self.__repr__()

    def __call__(self, **kwargs):
        # TODO: check me / document me
        for plugin in self:
            # Fixme: Recheck after rework of metadata
            if not hasattr(plugin, "metadata"):
                continue

            skip_iteration = False
            for key, value in kwargs.items():
                if plugin.metadata.get(key) != value:
                    skip_iteration = True
                    continue
            if skip_iteration:
                continue
            yield plugin

    # =============== #
    # PRIVATE METHODS #
    # =============== #
    def _register_base_plugin(self, base_plugin: T):
        # -- Check base clas is Plugin -- #
        if not issubclass(base_plugin, Plugin):
            raise TypeError(
                f"base_plugin '{base_plugin}' must be a subclass of '{Plugin}'"
            )

        # TODO: check that BasePlugin is not used otherwise
        # -- Check Metadata is well formed --
        # TODO: add testings for this section
        baseplugin_metadata_cls = getattr(base_plugin, "Metadata", None)
        if baseplugin_metadata_cls is not None:
            if not isinstance(baseplugin_metadata_cls, type):
                raise TypeError(f"Metadata for '{base_plugin}' must be a class")

            for e in dir(baseplugin_metadata_cls):
                if e.startswith("__"):
                    continue
                if e not in METADATA_ATTRIBUTES_NAMES:
                    raise AttributeError(
                        f"Metadata attribute {base_plugin.__name__}.Metadata.{e} is not recognized"
                    )

        # add all the constraints to the __koalak__.constraints dict and remove the field attributes
        self._add_constraints_to_cls(base_plugin)

        # All custom plugins (loaded from home) have _is_home_plugin to True
        # TODO: Now it's on Metadata! so we have to fix this
        self._base_plugin._is_home_plugin = False

        # This key is used to refere plugin_manager in base plugins
        # and to know when to validate or not plugin in Plugin.__init_subclass__
        setattr(base_plugin, KEY_PLUGIN_MANAGER, self)

    def _iter_constraints(self, plugin):
        """Return iterators of all constraints related to a plugin
        attributes, abstract methods)"""
        # Check both attributes constraints and metadata constraints
        for key_constraints in [KEY_METADATA_CONSTRAINTS, KEY_ATTRIBUTES_CONSTRAINTS]:
            seen_attributes = set()
            # Check constraints in parent classes also, but if overwritten do not return
            for cls in plugin.mro():
                cls_constraints = getattr(cls, key_constraints, None)
                if not cls_constraints:
                    continue

                for attribute_name, constraint in cls_constraints.items():
                    if attribute_name not in seen_attributes:
                        yield constraint
                        seen_attributes.add(attribute_name)

    def _init_home(self):
        for dir_path in [
            self.home_path,
            self.home_plugins_path,
            self.home_data_path,
            self.exceptions_path,
        ]:
            if not dir_path:
                continue
            elif not os.path.exists(dir_path):
                os.makedirs(dir_path)
            elif os.path.isfile(dir_path):
                raise NotADirectoryError(f"Path {dir_path} is not a directory")

    def _load_plugins(self):
        # TODO: read me again
        # TODO add security check when thinking about this program runnign as root?
        """Load home plugins"""
        if not self.home_path:
            return
        for python_path in glob.glob(os.path.join(self.home_plugins_path, "*.py")):
            with open(python_path) as f:
                data = f.read()
                execution_context = {}
                exec(data, execution_context)
                for object_name, object in execution_context.items():
                    if inspect.isclass(object) and issubclass(
                        object, self._base_plugin
                    ):
                        if object is self._base_plugin:
                            continue
                        object._is_home_plugin = True

    def _init_config(self):
        if self.config is None:
            return
        self.config.update_without_overwrite(self._config_dict_form_plugins)

    def _add_constraints_to_cls(self, cls):
        """Check class (base_class and abstract classes) to add constraints

        Add attributes constraints
        Add metadata constraints
        Add abstract methods constraints
        """
        cls_annotations = getattr(cls, "__annotations__", {})
        # Get constraints attribute #
        # ------------------------- #
        attributes_constraints = {}
        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)

            # If KEY_ABSTRACT_METHOD is present, that mean it's an abstract method
            if KEY_ABSTRACT_METHOD in dir(attribute):
                abstract_method_constraint = AbstractMethodConstraint(attribute_name)
                attributes_constraints[attribute_name] = abstract_method_constraint
            # Check attributes constraints
            elif isinstance(attribute, FieldDescription):
                attribute.name = attribute_name
                # If annotation is empty, add it from cls.__annotations__
                if attribute.annotation is None:
                    attribute.annotation = cls_annotations.get(attribute_name)
                attributes_constraints[attribute_name] = AttributeConstraint(attribute)
        if attributes_constraints:
            setattr(cls, KEY_ATTRIBUTES_CONSTRAINTS, attributes_constraints)

        # Metadata attributes
        baseplugin_metadata_cls = getattr(cls, "Metadata", None)
        if baseplugin_metadata_cls is not None:
            metadata_constraints = {}
            for attribute_name in dir(baseplugin_metadata_cls):
                attribute = getattr(baseplugin_metadata_cls, attribute_name)
                if isinstance(attribute, FieldDescription):
                    attribute.name = attribute_name
                    # If annotation is empty, add it from cls.__annotations__
                    if attribute.annotation is None:
                        attribute.annotation = cls_annotations.get(attribute_name)
                    metadata_constraints[attribute_name] = AttributeConstraint(
                        attribute, is_metadata=TypeVar
                    )
            if metadata_constraints:
                setattr(cls, KEY_METADATA_CONSTRAINTS, metadata_constraints)

    def _check_config_fields(self, cls):
        for attribute_name in dir(cls):
            attribute = getattr(cls, attribute_name)
            if not isinstance(attribute, ConfigDescription):
                continue

            if self.config is None:
                raise ValueError(
                    f"Can not use config_field with out path_config in the plugin manager"
                )
            # Add name of config field is empty
            if attribute.name is None:
                attribute.name = attribute_name

            if cls.name not in self._config_dict_form_plugins:
                self._config_dict_form_plugins[cls.name] = {}
            self._config_dict_form_plugins[cls.name][attribute.name] = attribute.default
            # TODO: check that config file exists
            # TODO: double check if ConfigDescription will not be added as a description
            try:
                default_value = self.config[cls.name][attribute.name]
            except KeyError:
                default_value = attribute.default

            setattr(cls, attribute_name, default_value)

    # Utils functions
    def print_table(self):
        # Fixme, print metadata fix it?
        metadata_fields = [e.field for e in self.metadata.values()]
        column_names = [e.name for e in metadata_fields]

        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(title=self.name)
        table.add_column("name")
        for column_name in column_names:
            table.add_column(column_name)

        for plugin in self:
            row = [plugin.name or ""]
            for field_name in column_names:
                cell = getattr(plugin.metadata, field_name)
                if cell is None:
                    cell = ""
                elif isinstance(cell, list):
                    cell = ", ".join(cell)
                else:
                    cell = str(cell)
                row.append(cell)
            table.add_row(*row)
        console.print(table)
