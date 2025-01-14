# Next Steps

The `plugin_manager` module is still under development, with several key features planned for future versions. Here are some enhancements we aim to implement, if time allows:

- **Selective Loading**: In applications with a large number of plugins, it can be beneficial to load only the required plugins to speed up startup. Selective loading will enable loading plugins based on specific metadata, such as `pm.load_plugins(category="windows")`.

- **Plugin Hubs**: The Plugin Hubs feature will enable the installation of plugins from remote platforms, similar to package managers like `apt` or Docker hubs. This will allow plugins to be shared through public repositories on platforms like GitHub or GitLab, or private repositories in internal Git systems.

- **Signature Verification for Abstract Methods**: An option will be introduced to enforce the checking of method signatures for abstract methods, improving consistency and reducing errors in subclass implementations (e.g., `@abstract(check_signature=True)`).

- **Plugin Execution Order**: The `plugins_precedence` feature will allow specifying the order in which plugins should be executed, ensuring correct execution flow by defining that certain plugins run before others.
