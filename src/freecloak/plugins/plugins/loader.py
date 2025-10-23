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


import importlib
import logging
import pkgutil
from types import ModuleType

import freecloak.plugins
from freecloak.plugins.logging import TemplateStringAdapter


logger = TemplateStringAdapter(logging.getLogger(__name__))


def discover_plugins() -> dict[str, ModuleType]:
    iter_namespace = lambda ns_pkg: pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    discovered_plugins = {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespace(freecloak.plugins)
    }

    valid_plugins = {}

    for plugin_name, plugin_module in discovered_plugins.items():
        if not hasattr(plugin_module, '__plugin_info__'):
            logger.warning(t'Plugin {plugin_name} has no __plugin_info__ attribute, skipping')
            continue

        valid_plugins[plugin_name] = plugin_module

    return valid_plugins