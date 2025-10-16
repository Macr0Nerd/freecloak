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
from typing import Callable


def level_and_below_filter(level: int | str) -> Callable[[logging.LogRecord], bool]:
    if isinstance(level, str):
        level = getattr(logging, level.upper())

    def _filter(record: logging.LogRecord) -> bool:
        return record.levelno <= level

    return _filter


filters = {
    'level_below': {
        logging.NOTSET: level_and_below_filter(logging.NOTSET),
        logging.DEBUG: level_and_below_filter(logging.DEBUG),
        logging.INFO: level_and_below_filter(logging.INFO),
        logging.WARNING: level_and_below_filter(logging.WARNING),
        logging.ERROR: level_and_below_filter(logging.ERROR),
        logging.CRITICAL: level_and_below_filter(logging.CRITICAL),
    }
}