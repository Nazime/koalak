from pathlib import Path
from typing import Any, Dict, Union

import toml
from koalak.utils import dict_update_without_overwrite


class Config:
    """Configuration handler using TOML files."""

    def __init__(
        self,
        path: Union[Path, str],
        *,
        default_data: Dict[str, Any] = None,
        empty_as_none: bool = None,
        _section: str = None,
        _data: dict = None,
        _root: "Config" = None,
    ):
        """
        Initializes the configuration with optional default data.

        Args:
            path: Path to the configuration file.
            default_data: Default data to ensure specific sections/keys exist.
            empty_as_none: If True, treat empty strings in TOML as None values.
        """
        if empty_as_none is None:
            empty_as_none = False

        if _section is None:
            _section = ""

        self.path = Path(path).expanduser()
        self.section = _section
        self.empty_as_none = empty_as_none
        self._root_config: Config = _root

        if _data is not None:
            self._data = _data
        elif self.path.exists():
            self._data = self.load()
        else:
            self._data = {}

        if default_data:
            self.update_without_overwrite(default_data)
            self.save()

    def load(self) -> Dict[str, Any]:
        """Loads the configuration file."""
        # FIXME: what if we do .load() from a nested config
        with open(self.path, "r") as file:
            data = toml.load(file)
            if self.empty_as_none:
                self.convert_empty_strings_to_none(data)
            return data

    def convert_empty_strings_to_none(self, data: Dict[str, Any]):
        """Converts empty strings in the data to None."""
        for section in data.values():
            for key, value in section.items():
                if value == "":
                    section[key] = None

    def update_without_overwrite(self, data: dict):
        """Merges default data without overwriting existing values."""
        """
        Merges the provided default data with the existing configuration data.
        New keys and sections are added, but existing values are not overwritten.

        Args:
            default_data: A dictionary containing the default configuration data.
        """
        dict_update_without_overwrite(self._data, data)
        self.save()

    def save(self):
        """Saves the current configuration to file.
        Will always save the root config and not the section only"""
        if self._root_config is None:
            with open(self.path, "w") as file:
                toml.dump(self._data, file)
        else:
            self._root_config.save()

    def __getitem__(self, key: str) -> Any:
        """Retrieves a specific configuration section."""
        value = self._data[key]
        if isinstance(value, dict):
            if self.section:
                section = f"{self.section}.{key}"
            else:
                section = key

            if self._root_config is None:
                root = self
            else:
                root = self._root_config

            value = Config(self.path, _section=section, _data=value, _root=root)
        return value

    def __setitem__(self, key: str, value: Any):
        """Sets an item in the section."""
        if self.empty_as_none and value == "":
            value = None
        self._data[key] = value
        self.save()

    def __contains__(self, key: str) -> bool:
        """
        Checks if a key or section exists in the configuration.

        Args:
            key: The key or section name to check for existence.

        Returns:
            bool: True if the key or section exists, False otherwise.
        """
        return key in self._data

    def __delitem__(self, key: str):
        """
        Deletes a key or section from the configuration.

        Args:
            key: The key or section name to delete.
        """
        del self._data[key]
        self.save()

    def __str__(self) -> str:
        if self.section:
            str_section = f":{self.section}"
        else:
            str_section = ""
        return f"Config('{self.path}{str_section}')"

    def __repr__(self):
        return self.__str__()

    # Copying dict API
    def keys(self):
        return self._data.keys()

    def items(self):
        for k in self._data.keys():
            yield k, self[k]

    def values(self):
        for k in self._data.keys():
            yield self[k]

    def __iter__(self):
        yield from self.keys()


# TODO: continue implementing and testing nested sections
# TODO: implement and test empty_as_none (convert_empty_strings_to_none is not working)
# TODO: implement default value from config file (use same value default_data)
