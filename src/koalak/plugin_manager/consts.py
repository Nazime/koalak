# -- KEYS -- #
# ========== #
# KEY are attributes name to store inside plugins and base_plugin for internal
#  plugin_manager to work

# Attribute injected inside abstract methods
KEY_ABSTRACT_METHOD = "__koalak_abstract_method__"
# Attribute injected inside base_plugin
KEY_PLUGIN_MANAGER = "__koalak_plugin_manager__"
# Store all constraints (abstract method and attributes) in a nested dict
KEY_ATTRIBUTES_CONSTRAINTS = "__koalak_attributes_constraints__"
KEY_METADATA_CONSTRAINTS = "__koalak_metadata_constraints__"

# TODO: implement metadata
KEY_METADATA_DEFAULT_VALUES = "__koalak_metadata_default_values__"
