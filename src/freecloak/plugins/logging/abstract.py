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
import string.templatelib
from typing import Mapping, Optional


class TemplateStringAdapterWrapper:
    def __init__(self, template: string.templatelib.Template | str):
        self.template = template

    def __str__(self) -> str:
        if isinstance(self.template, str):
            return self.template

        return ''.join(map(lambda x: x.value if isinstance(x, string.templatelib.Interpolation) else x, iter(self.template)))


class TemplateStringAdapter(logging.LoggerAdapter):
    def process(self, msg: string.templatelib.Template, kwargs: None) -> tuple[TemplateStringAdapterWrapper, Optional[Mapping]]:
        if kwargs:
            raise AttributeError('kwargs cannot be used with the template string adapter')

        return TemplateStringAdapterWrapper(msg), kwargs
