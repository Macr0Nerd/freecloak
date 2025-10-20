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


import datetime
import logging
from typing import Optional

import requests
import requests.auth

from freecloak.plugins.logging import TemplateStringAdapter


logger = TemplateStringAdapter(logging.getLogger(__name__))


class KeycloakAuth(requests.auth.AuthBase):
    def __init__(self, client_id: str, client_secret: str, token_endpoint: str) -> None:
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.token_endpoint: str = token_endpoint

        self.token: Optional[str] = None
        self.token_expires: Optional[datetime.datetime] = None
        self.token_type = None

    def __call__(self, r):
        if not self.token_expires or self.token_expires < datetime.datetime.now():
            self.refresh_token()

        r.headers['Authorization'] = f'{self.token_type} {self.token}'
        return r

    def refresh_token(self) -> None:
        authentication_data = requests.post(
            self.token_endpoint,
            data={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials',
            }
        ).json()

        self.token = authentication_data['access_token']
        self.token_type = authentication_data['token_type']
        self.token_expires = datetime.datetime.now() + datetime.timedelta(seconds=authentication_data['expires_in'])
