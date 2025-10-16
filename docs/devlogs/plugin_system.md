# Plugin System
The plugin system will hopefully allow for extensions on top of freecloak
to make managing the FreeIPA & Keycloak integration easier. The plugin system
mostly pulls from the (Python Packaging User Guide)[https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-namespace-packages],
but freecloak expects plugins to be formatted a specific way.

A guide for creating plugins to be imported will be made later, but plugins
are going to be the base for freecloak. These plugins will implement the tools
for interacting with data in both Keycloud and FreeIPA simultaneously. This is
initially being built as a CLI tool, but while potentially be built upon with
more management tools and automation improvements.

While plugins are being dynamically loaded, they are checked to ensure that
they provide `__plugin_info__`, which is some basic metadata about the plugin.
This is all that is needed for a plugin to be recognized. If you want a plugin
to be usable from the cli, you must implement an `<your plugin>.cli` with the
`add_plugin_parser` method that will be the entrypoint for adding argparse
arguments. This method will be passed a `argparse._SubParsersAction` 