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


import logging

from freecloak.plugins.logging import TemplateStringAdapter
from freecloak.plugins.plugins import PluginInfo
from freecloak.plugins.plugins.loader import discover_plugins


logger = TemplateStringAdapter(logging.getLogger(__name__))


def list(**_) -> int:
    discovered_plugins = discover_plugins()

    print(f'{'Name':<15} {'Version':<15} {'Description'}')
    print(f'{'=' * 15} {'=' * 15} {'=' * 15}')

    for plugin_path, plugin_module in discovered_plugins.items():
        plugin_info: PluginInfo = plugin_module.__plugin_info__
        name = plugin_info.plugin_name
        version = plugin_info.plugin_version
        description = plugin_info.plugin_description
        print(f'{name:<15} {version if version else '':<15} {description if description else ''}')

    return 0