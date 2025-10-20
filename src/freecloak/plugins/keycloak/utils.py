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
from typing import Optional

import requests_toolbelt.sessions

from freecloak.plugins.logging import TemplateStringAdapter
from freecloak.plugins.exceptions import FreecloakExitError

from freecloak.plugins.keycloak.abstract import KeycloakAuth


logger = TemplateStringAdapter(logging.getLogger(__name__))


def get_base_url(
    domain: str,
    *,
    allow_insecure: Optional[bool] = None,
    port: Optional[int] = None,
    **_
) -> str:
    schema = 'https'
    if allow_insecure:
        logger.warning('You are connecting to Keycloak using an insecure connection!')
        schema = 'http'

    base_url = f'{schema}://{domain}'

    if port is not None:
        if port == 0 or port > 65535:
            logger.error('Invalid port number specified; exiting')
            raise FreecloakExitError

        base_url += f':{port}'

    base_url += '/'

    return base_url

def get_client_secret(client_secret_file: str, **_) -> str:
    try:
        with open(client_secret_file) as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error('Client secret file not found; exiting')
        raise FreecloakExitError

def get_session(realm: str, *_, **kwargs) -> requests_toolbelt.sessions.BaseUrlSession:
    try:
        base_url = get_base_url(**kwargs)
    except FreecloakExitError:
        raise

    try:
        client_secret = get_client_secret(**kwargs)
    except FreecloakExitError:
        raise

    # ToDo: Configure error handling
    s = requests_toolbelt.sessions.BaseUrlSession(base_url)
    openid_configuration = s.get(f'realms/{realm}/.well-known/openid-configuration').json()
    token_endpoint = openid_configuration['token_endpoint']

    s.auth = KeycloakAuth(kwargs['client_id'], client_secret, token_endpoint)

    return s