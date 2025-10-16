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


import os
import sys


if not __package__:
    package_source_path = os.path.dirname(os.path.dirname(__file__))
    sys.path[0] = package_source_path

if __name__ == "__main__":
    from freecloak.cli import main
    sys.exit(main())