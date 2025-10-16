##############################################################################
##  Copyright (C) 2025  Gabriele Ron                                        ##
##                                                                          ##
##  This program is free software: you can redistribute it and/or modify    ##
##  it under the terms of the GNU General Public License as published by    ##
##  the Free Software Foundation, either version 3 of the License, or       ##
##  (at your option) any later version.                                     ##
##                                                                          ##
##  This program is distributed in the hope that it will be useful,         ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of          ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           ##
##  GNU General Public License for more details.                            ##
##                                                                          ##
##  You should have received a copy of the GNU General Public License       ##
##  along with this program.  If not, see <https://www.gnu.org/licenses/>.  ##
##############################################################################


import argparse
import importlib
import logging

from freecloak import __version__
from freecloak.plugins.abstract import PluginInfo
from freecloak.plugins.logging import configure_logging, TemplateStringAdapter
from freecloak.plugins.utils import discover_plugins


logger = TemplateStringAdapter(logging.getLogger(__name__))


def add_connection_arguments(parser: argparse.ArgumentParser) -> None:
    keycloak_group = parser.add_argument_group('keycloak')

def add_miscellaneous_arguments(parser: argparse.ArgumentParser) -> None:
    miscellaneous_group = parser.add_argument_group('miscellaneous')

    miscellaneous_group.add_argument('-h', '--help', action='help')
    miscellaneous_group.add_argument('-V', '--version', action='version', version=f'freecloak v{__version__}')

def add_logging_arguments(parser: argparse.ArgumentParser) -> None:
    console_logging_group = parser.add_argument_group('console logging options')

    console_logging_group_me = console_logging_group.add_mutually_exclusive_group()
    console_logging_group_me.add_argument('-v', '--verbose', help='increase console log level', action='count')
    console_logging_group_me.add_argument('-q', '--quiet', help='decrease console log level', action='count')

    console_logging_group.add_argument('--suppress-stdout', action='store_true')


    file_logging_group = parser.add_argument_group('file logging options')
    file_logging_group.add_argument('--output-log-file', help='main log file to use', metavar='FILE')
    file_logging_group.add_argument('--output-log-level', help='file logging level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])

def main() -> int:
    root_parser = argparse.ArgumentParser(
        prog="freecloak",
        description="FreeIPA and Keycloak integration tool",
        epilog="Built & Developed by Gabriele Ron (developer@groncyber.com)",
        add_help=False,
    )

    # Configure logging first so we can use it when discovering plugins if necessary
    add_logging_arguments(root_parser)
    logging_args, cli_args = root_parser.parse_known_args()
    configure_logging(**vars(logging_args))

    plugins = discover_plugins()

    global_arg_funcs = [add_logging_arguments, add_miscellaneous_arguments]
    subparsers = root_parser.add_subparsers(help='plugin help', dest='plugin', metavar='PLUGIN', required=True)
    for plugin_name, plugin_module in plugins.items():
        plugin_info: PluginInfo = plugin_module.__plugin_info__

        try:
            plugin_cli_module = importlib.import_module(f'{plugin_name}.cli')
            plugin_parser_func = plugin_cli_module.add_plugin_parser

            plugin_parser = subparsers.add_parser(plugin_info.plugin_name, help=f'{plugin_info.plugin_name} help', add_help=False)
            plugin_subparsers = plugin_parser.add_subparsers(help='command help', dest='command', metavar='COMMAND', required=True)

            plugin_parser_func(plugin_subparsers, global_arg_funcs=global_arg_funcs)
        except AttributeError:
            logger.warning(t'Plugin {plugin_info.plugin_name} does not properly implement the plugin specification; skipping')
            continue
        except ImportError:
            logger.debug(t'Plugin {plugin_info.plugin_name} is a backend plugin; skipping')
            continue

        for global_arg_func in global_arg_funcs:
            global_arg_func(plugin_parser)

    add_miscellaneous_arguments(root_parser)

    args = vars(root_parser.parse_args())

    try:
        plugin_commands_module = importlib.import_module(f"freecloak.plugins.{args['plugin']}.commands")
        return getattr(plugin_commands_module, args['command'])(**args)
    except AttributeError:
        logger.error(t'Plugin "{args["plugin"]}" has no command "{args["command"]}"')
        return 2
    except ImportError:
        logger.error(t'Plugin "{args["plugin"]}" does not properly implement the plugin specification; exiting')
        return 1
