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
import logging

from freecloak.plugins.logging import TemplateStringAdapter


logger = TemplateStringAdapter(logging.getLogger(__name__))


def add_connection_arguments(parser: argparse.ArgumentParser) -> None:
    keycloak_connection_group = parser.add_argument_group('keycloak connection')
    keycloak_connection_group.add_argument('-d', '--domain', help='keycloak domain', required=True)
    keycloak_connection_group.add_argument('-p', '--port', help='keycloak port', type=int)
    keycloak_connection_group.add_argument('-r', '--realm', help='keycloak realm', required=True)

    keycloak_connection_group.add_argument('-cid', '--client-id', help='keycloak client id', required=True)
    keycloak_connection_group.add_argument('-csf', '--client-secret-file', help='keycloak client secret file path', required=True)

    keycloak_connection_group.add_argument('--insecure', help='use HTTP to connect', action="store_true")

    pass

def add_plugin_parser(subparsers: argparse._SubParsersAction) -> None:
    dev_parser = subparsers.add_parser('dev')
    add_connection_arguments(dev_parser)
