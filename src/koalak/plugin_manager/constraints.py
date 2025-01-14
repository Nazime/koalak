import abc

from koalak.descriptions.field_description import FieldDescription

from .consts import KEY_ABSTRACT_METHOD
from .utils import ConstraintDescription


class BaseConstraint(abc.ABC):
    """Base class to implement constraints on plugins (having specific attribute, abstract method, etc)"""

    @abc.abstractmethod
    def check(self, obj):
        """Main method to define, this method must raise errors when encountering
            none respected constraints

        Args:
            obj: obj to check against"""
        pass


# ==================== #
# BUILT-IN Constraints #
# ==================== #


class AttributeConstraint(BaseConstraint):
    """Check if a specific attribute is present or not on subclass, also check
    - its type
    - choices
    - min/max
    Works for both direct attributes and metadata attributes
    """

    def __init__(self, field: FieldDescription, is_metadata=None):
        """
        Args:
            field: description to check (take name, type and choices into account)
        """
        if is_metadata is None:
            is_metadata = False
        self.is_metadata = is_metadata
        self.field = field

    def check(self, plugin):
        # TODO: if it's metadata, check if type are good or not
        # Determine the target object for attribute checks
        target = getattr(plugin, "metadata") if self.is_metadata else plugin
        target_type = "metadata" if self.is_metadata else "class"

        # Check if attribute is present
        if not hasattr(target, self.field.name):
            raise AttributeError(
                f"Field {self.field.name!r} not present in {target_type} attributes of plugin {plugin.__name__!r}"
            )

        plugin_attr = getattr(target, self.field.name)
        if isinstance(plugin_attr, ConstraintDescription):
            raise AttributeError(
                f"Field {self.field.name!r} not present in {target_type} attributes of plugin {plugin.__name__!r}"
            )

        # Check type
        if self.field.type is not None and not self.field.check(plugin_attr):
            raise TypeError(
                f"{target_type.capitalize()} attribute {self.field.name!r} must be of type "
                f"{self.field.type!r}, not {type(plugin_attr)}"
            )

        # Check choices
        if self.field.choices and plugin_attr not in self.field.choices:
            raise ValueError(
                f"{target_type.capitalize()} attribute {self.field.name!r} must be in {self.field.choices!r}"
            )

        # Check min value
        if self.field.min is not None and plugin_attr < self.field.min:
            raise ValueError(
                f"{target_type.capitalize()} attribute {self.field.name!r} must be >= {self.field.min}, but got {plugin_attr}"
            )

        # Check max value
        if self.field.max is not None and plugin_attr > self.field.max:
            raise ValueError(
                f"{target_type.capitalize()} attribute {self.field.name!r} must be <= {self.field.max}, but got {plugin_attr}"
            )

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.field.name})>"


class AbstractMethodConstraint(BaseConstraint):
    """Check if abstract method is implemented or not"""

    def __init__(self, method_name):
        self.method_name = method_name

    def check(self, plugin):
        # To check if abstract method is implemented, we have to check in the object if it have
        # the attribute __koalak_abstract__

        method = getattr(plugin, self.method_name)
        if getattr(method, KEY_ABSTRACT_METHOD, False):
            raise AttributeError(
                f"Plugin {plugin.__name__!r} have an abstract method {self.method_name!r}"
            )

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.method_name})>"
