from koalak.descriptions import FieldDescription

from .consts import KEY_ABSTRACT_METHOD


def abstract(obj):
    """Male method as abstract method to add it as a plugin constraint"""
    # Only add KEY_ABSTRACT_METHOD in the method attributes, and then when checking
    #  the plugin, we will see if the attribute is present or not (new method defined)
    setattr(obj, KEY_ABSTRACT_METHOD, True)
    return obj


class ConstraintDescription(FieldDescription):
    # Inherit from FieldDescription to be able to use isinstance(obj, ConstraintDescription)
    pass


field = ConstraintDescription
