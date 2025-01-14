from koalak.plugin_manager import Plugin

_name_counter = 0


def get_unique_name():
    global _name_counter
    _name_counter += 1
    return f"__unique_name_{_name_counter}"


def get_unique_base_plugin():
    class BasePlugin(Plugin):
        pass

    return BasePlugin
