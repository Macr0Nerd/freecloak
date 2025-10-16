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
import logging.config
from typing import Optional

from freecloak.plugins.logging.filters import filters


def configure_logging(
    *,
    output_log_file: Optional[str] = None,
    output_log_level: Optional[str | int] = None,
    quiet: Optional[int] = None,
    verbose: Optional[int] = None,
    suppress_stdout: Optional[bool] = None,
    **_
) -> None:
    if output_log_level is None:
        output_log_level = logging.INFO
    elif isinstance(output_log_level, str):
        output_log_level = getattr(logging, output_log_level.upper())

    if quiet and verbose:
        raise ValueError('the quiet and verbose options are mutually exclusive')

    console_log_level = logging.WARNING

    if quiet:
        console_log_level += min(quiet * 10, 20)
    elif verbose:
        console_log_level -= min(verbose * 10, 20)

    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '({asctime}) {name} [{levelname}]: {message}',
                'datefmt': '%H:%M:%S',
                'style': '{',
                'validate': True
            },
            'file': {
                'format': '{asctime} {name} {levelname}: {message}',
                'datefmt': '%Y-%m-%d %H:%M:%S',
                'style': '{',
                'validate': True
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'level': console_log_level,
                'formatter': 'console',
                'stream': 'ext://sys.stdout',
                'filters': [filters['level_below'][logging.WARNING]],
            },
            'stderr': {
                'class': 'logging.StreamHandler',
                'level': logging.ERROR,
                'formatter': 'console',
                'stream': 'ext://sys.stderr',
            },
        },
        'root': {
            'level': logging.DEBUG,
            'handlers': ['stdout', 'stderr'],
        }
    }

    if suppress_stdout:
        logging_config['root']['handlers'].remove('stdout')

    if output_log_file:
        logging_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': output_log_level,
            'formatter': 'file',
            'filename': output_log_file,
        }

        logging_config['root']['handlers'].append('file')

    logging.config.dictConfig(logging_config)
