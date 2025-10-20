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
This is all that is needed for a plugin to be recognized. Any commands that the
plugin will run must be declared in `<plugin>.commands`.

If you want a plugin to be usable from the cli, you must implement an
`<plugin>.cli` with the `add_plugin_parser` method that will be the
entrypoint for adding argparse arguments. This method will be passed a
`argparse._SubParsersAction` so that it can add the cli commands and
configuration options. When creating your argument parsers, keep in mind that
the global logging argument groups will be added to all subparsers (both plugin
and command). Additionally, the commands added must be accessible from the
module path `<plugin>.commands` or they will not be found. These commands
should accept kwargs, although they do not need to be used (e.g. `**_`).