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
from typing import Optional, Self

import requests_toolbelt.sessions

from freecloak.plugins.exceptions import FreecloakExitError
from freecloak.plugins.logging import TemplateStringAdapter

from freecloak.plugins.keycloak.auth import KeycloakAuth


logger = TemplateStringAdapter(logging.getLogger(__name__))


class KeycloakSession:
    __slots__ = [
        'base_url',
        'realm',
        'client_id',
        'client_secret',
        'session',
    ]

    def __init__(
        self,
        *,
        domain: str,
        port: Optional[int] = None,
        realm: str,
        client_id: str,
        client_secret: Optional[str] = None,
        client_secret_file: Optional[str] = None,
        session: Optional[requests_toolbelt.sessions.BaseUrlSession] = None,
        allow_insecure: Optional[bool] = None,
        **_,
    ):
        schema = 'https'
        if allow_insecure:
            logger.warning('You are connecting to Keycloak using an insecure connection!')
            schema = 'http'

        if port is not None:
            if port == 0 or port > 65535:
                logger.error('Invalid port number specified; exiting')
                raise FreecloakExitError

        self.base_url = f'{schema}://{domain}{f':{port}' if port else ''}/'
        self.realm = realm
        self.client_id = client_id

        if client_secret:
            self.client_secret = client_secret
        elif client_secret_file:
            try:
                with open(client_secret_file) as f:
                    self.client_secret = f.read().strip()
            except FileNotFoundError:
                logger.error('Client secret file not found; exiting')
                raise FreecloakExitError
        else:
            logger.info('No client secret specified; exiting')
            raise FreecloakExitError

        self.session = session

    def __enter__(self):
        if not self.session:
            self.create_session()

        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.session = None

    def __get__(self, instance: KeycloakClient, owner=None):
        if not self.session:
            self.create_session()

        return self.session

    def __set__(self, instance: KeycloakClient, value: Optional[KeycloakSession]):
        if not value and self.session:
            self.session.close()
            self.session = None
            return

        self.base_url = value.base_url
        self.realm = value.realm
        self.client_id = value.client_id
        self.client_secret = value.client_secret
        self.session = value.session

    def __getattr__(self, item):
        if item == 'close':
            close_func = self.session.close
            self.session = None
            return close_func

        if not self.session:
            self.create_session()

        return getattr(self.session, item)

    def create_session(self):
        self.session = requests_toolbelt.sessions.BaseUrlSession(self.base_url)
        openid_configuration = self.session.get(f'realms/{self.realm}/.well-known/openid-configuration').json()
        token_endpoint = openid_configuration['token_endpoint']

        self.session.auth = KeycloakAuth(self.client_id, self.client_secret, token_endpoint)


class KeycloakClient:
    __slots__ = ['realm', 'session']

    realm: str
    session: KeycloakSession

    def __init__(self, realm: str, **kwargs):
        self.realm = realm
        self.session = KeycloakSession(realm=realm, **kwargs)

    def __getattribute__(self, item):
        pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session = None
