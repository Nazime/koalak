# Introduction

## Overview

The **Plugin Manager** (`plugin_manager`) is the core module of the `koalak` library, designed to facilitate the development of applications with a plugin-based architecture.
It provides a structured and efficient way to manage plugins by reducing boilerplate and offering streamlined default functionality.

## Key Features

- **Enforced Plugin Constraints**: Ensures plugins comply with predefined rules at class creation, such as:
    - Implementing specific methods (abstract methods at class definition).
    - Including required attributes with specific types.
    - Enforce required metadata (e.g., category, description, version, authors)

- **Plugin Metadata**: Enables plugin metadata with features:
    - Allows filtering plugins by metadata (e.g., description, category, tags, version, authors).
    - Controls plugin sequence using `metadata.order`.
    - Verifies plugin dependencies, including Python libraries and executable dependencies in the system's PATH.

- **Home Plugin Loading**: Supports loading user-defined plugins from a dedicated home directory, allowing customization without modifying the core application.
  Example: Loading plugins from `~/.myapp/plugins/`.

- **Customizing Plugin Attributes**: Enables the customization of plugin settings through `.toml` configuration files, such as `~/.myapp/plugins/plugins.toml`. This allows loading and overriding plugin attributes at runtime, providing flexibility to adjust plugin behavior for different environments or user configurations.
