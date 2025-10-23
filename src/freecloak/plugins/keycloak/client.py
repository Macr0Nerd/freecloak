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
from importlib.resources import files
import itertools
import json
import logging
from typing import Any, Callable, Iterable, Self

import requests_toolbelt.sessions

from freecloak.plugins.logging import TemplateStringAdapter

from freecloak.plugins.keycloak.auth import KeycloakAuth
from freecloak.plugins.keycloak.exceptions import *


logger = TemplateStringAdapter(logging.getLogger(__name__))


MODEL_DATA_TYPES = {
    'array': Iterable,
    'boolean': bool,
    'integer': int,
    'number': float,
    'object': object,
    'string': str,
}


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
                raise KeycloakClientError

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
                raise KeycloakClientError
        else:
            logger.info('No client secret specified; exiting')
            raise KeycloakClientError

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
        logger.debug('Creating new Keycloak session')

        self.session = requests_toolbelt.sessions.BaseUrlSession(self.base_url)
        openid_configuration = self.session.get(f'realms/{self.realm}/.well-known/openid-configuration').json()
        token_endpoint = openid_configuration['token_endpoint']

        self.session.auth = KeycloakAuth(self.client_id, self.client_secret, token_endpoint)

        logger.debug('Keycloak session created')


class KeycloakClient:
    __slots__ = [
        'action_map',
        'model',
        'realm',
        'session',
    ]

    action_map: dict
    model: dict
    realm: str
    session: KeycloakSession

    def __init__(self, realm: str, **kwargs):
        data_files = files('freecloak.plugins.keycloak.data')
        self.action_map = json.loads(data_files.joinpath('action_map.json').read_text('utf-8'))
        self.model = json.loads(data_files.joinpath('keycloak-openapi-1.0.json').read_text('utf-8'))

        self.realm = realm
        self.session = KeycloakSession(realm=realm, **kwargs)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session = None

    def __getattr__(self, item) -> Callable:
        try:
            action = self.action_map[item]
        except KeyError:
            logger.warning(f'Keycloak action {item} not found; exiting')
            raise KeycloakClientError

        path = action['path']
        method = action['method']

        path_method_info = self.model['paths'][path][method]

        request_model = dict()
        if path_method_info.get('requestBody'):
            reference = path_method_info['requestBody']['content']['application/json']['schema']['$ref']
            request_model = self.load_model(reference)

        response_model = {
            'type': 'object'
        }
        if '200' in path_method_info['responses']:
            path_method_response_schema = path_method_info['responses']['200']['content']['application/json']['schema']
            if response_type := path_method_response_schema.get('type'):
                response_model['type'] = response_type

                if response_type == 'array':
                    if response_item_type := path_method_response_schema['items'].get('type'):
                        response_model['item_type'] = response_item_type
                    elif response_item_ref := path_method_response_schema['items'].get('$ref'):
                        response_model['item_type'] = 'reference'
                        response_model['item_ref'] = response_item_ref
            elif response_ref := path_method_response_schema.get('$ref'):
                response_model['type'] = 'reference'
                response_model['ref'] = response_ref

        params = {
            convert_snake_case(param['name']): {
                'api_name': param['name'],
                'in': param['in'],
                'required': param.get('required', False),
                'type': MODEL_DATA_TYPES[param['schema']['type']],
            }
            for param
            in path_method_info['parameters']
        }

        if self.model['paths'][path].get('parameters'):
            params.update({
                convert_snake_case(param['name']): {
                    'api_name': param['name'],
                    'in': param['in'],
                    'required': param['required'],
                    'type': MODEL_DATA_TYPES[param['schema']['type']],
                }
                for param
                in self.model['paths'][path]['parameters']
            })

        def _api_callable(**kwargs) -> dict | list:
            if not kwargs:
                kwargs = {}

            param_groups = {
                'query': dict(),
                'path': dict(),
            }
            for param_name, param_data in params.items():
                param_val = kwargs.pop(param_name, None)

                if param_data['required'] and not param_val:
                    logger.error(t'Required parameter {param_name} not found; exiting')
                    raise KeycloakClientError

                if param_val:
                    if not isinstance(param_val, param_data['type']):
                        logger.error(t'Parameter {param_name} expects type {param_data['type']}, not {type(param_val)}; exiting')
                        raise KeycloakClientError

                    param_groups[param_data['in']][param_data['api_name']] = param_val

            request_kwargs = dict({
                'url': path.format(**param_groups['path'])
            })

            if query_params := param_groups['query']:
                request_kwargs['params'] = query_params

            if method in ['post', 'put']:
                kwargs = self.validate_model(request_model, kwargs)
                request_kwargs['data'] = kwargs

            response = self.session.request(method.upper(), **request_kwargs)
            response_description = path_method_info['responses'][str(response.status_code)]['description']

            match response.status_code:
                case 200:
                    return self.convert_model(response_model, response.json())
                case 201:
                    return {'return': True}
                case 204:
                    return {'return': True}
                case 400:
                    logger.error('This request is invalid; exiting')
                    raise KeycloakClientBadRequestError
                case 403:
                    logger.error('This request is forbidden; exiting')
                    raise KeycloakClientForbiddenError
                case 404:
                    logger.error('Invalid path; exiting')
                    raise KeycloakClientNotFoundError
                case 409:
                    logger.error('Conflicting data; exiting')
                    raise KeycloakClientConflictError
                case 500:
                    logger.error('Internal Server Error; exiting')
                    raise KeycloakClientServerError
                case _:
                    logger.error(t'Unexpected response from Keycloak server: {response_description}; exiting')
                    raise KeycloakClientError

        return _api_callable

    def load_model(self, ref: str) -> dict:
        position = self.model
        model_path = ref.split('/')[1:]
        for path in model_path:
            position = position.get(path)

            if not position:
                logger.error(t'Model could not be found at reference {ref}; exiting')
                raise KeycloakClientError

        model = dict()
        for name, metadata in position['properties'].items():
            program_name = convert_snake_case(name)

            model_data = {'api_name': name}

            if data_type := metadata.get('type'):
                model_data['type'] = data_type

                if data_type == 'array':
                    if item_data_type := metadata['items'].get('type'):
                        model_data['item_type'] = item_data_type
                    elif item_ref := metadata['items'].get('$ref'):
                        model_data['item_type'] = 'reference'
                        model_data['item_ref'] = item_ref
            elif ref := metadata.get('$ref'):
                model_data['type'] = 'reference'
                model_data['ref'] = ref

            if data_format := metadata.get('format'):
                model_data['format'] = data_format

            if (uniq := metadata.get('uniqueItems')) is not None:
                model_data['unique_items'] = uniq

            if (read_only := metadata.get('readOnly')) is not None:
                model_data['read_only'] = read_only

            model[program_name] = model_data

        return model

    def convert_model(self, model: dict, data: Any) -> Any:
        match model['type']:
            case 'array':
                match model['item_type']:
                    case 'reference':
                        return [self.convert_model({'type': 'reference', 'ref': model['item_ref']}, i) for i in data]
                    case _:
                        return data
            case 'reference':
                data_model = self.load_model(model['ref'])

                for key, key_model in data_model.items():
                    if key_data := data.pop(key_model['api_name'], None):
                        key_data = self.convert_model(key_model, key_data)
                        data[key] = key_data

                return data
            case _:
                return data

    def validate_model(self, model: dict, data: dict) -> dict:
        validated_data = dict()
        for key, value in data.items():
            if key not in model:
                logger.error(t'Invalid parameter {key}; exiting')
                raise KeycloakClientError

            key_data = model[key]

            if key_data['read_only']:
                logger.error(t'Parameter {key} is read only; exiting')
                raise KeycloakClientError

            match key_data_format := key_data.get('format'):
                case 'date':
                    if isinstance(value, datetime.date):
                        value = value.isoformat()
                case 'date-time':
                    if isinstance(value, datetime.datetime):
                        value = value.isoformat()
                case _:
                    pass

            match key_data_type := key_data['type']:
                case 'array':
                    if not isinstance(value, MODEL_DATA_TYPES[key_data_type]):
                        logger.error(t'Parameter {key} is not a proper array; exiting')
                        raise KeycloakClientError

                    match key_data_item_type := key_data['item_type']:
                        case 'reference':
                            key_data_item_model = self.load_model(key_data['item_ref'])
                            value = [self.validate_model(key_data_item_model, v) for v in value]
                        case _:
                            for v in value:
                                if not isinstance(v, MODEL_DATA_TYPES[key_data_item_type]):
                                    logger.error(t'Parameter {key} expects array elements to be type {key_data_item_type}; exiting')
                                    raise KeycloakClientError

                    if key_data['unique_items'] and len(value) > len(set(value)):
                        logger.error(t'Parameter {key} must have unique items; exiting')
                        raise KeycloakClientError
                case 'reference':
                    key_data_model = self.load_model(key_data['ref'])
                    value = self.validate_model(key_data_model, value)
                case _:
                    if not isinstance(value, MODEL_DATA_TYPES[key_data_type]):
                        logger.error(t'Parameter {key} expects type {key_data_type}, not {type(value)}; exiting')
                        raise KeycloakClientError

            validated_data[key_data['api_name']] = value

        return validated_data


def convert_snake_case(string: str) -> str:
    caps_indices = sorted(
        list(filter(lambda x: x is not None, map(lambda x: x[0] if x[1].isupper() else None, enumerate(string)))))
    caps_split_indices = [0]
    for k, g in itertools.groupby(enumerate(caps_indices), lambda x: x[1] - x[0]):
        g = list(g)
        start = g[0][1]
        end = g[-1][1]

        caps_split_indices.append(start)
        if start != end and end + 1 != len(string):
            caps_split_indices.append(end)

    caps_split_indices = list(set(caps_split_indices))
    parts = [string[i:j] for i, j in zip(caps_split_indices, caps_split_indices[1:] + [None])]
    snake_case_string = '_'.join(parts).lower().replace('-', '_')
    return snake_case_string
