# freecloak

 - [Overview](#overview)
 - [Installation](#installation)
 - [Usage](#usage)
 - [License](#license)
 - [Organization](#organization)

## Overview
Freecloak is a highly extensible framework for building tools to manage and
integrate FreeIPA and Keycloak. This project was born out of the desire to
seamlessly integrate these two systems such that Keycloak could fully manage
FreeIPA users. This better leaves FreeIPA to handle system authentication and
authorization, certificate and principal management, DNS, and service accounts.

This combination is already a scalable enterprise combination, but removing the
barriers between the two will enable a much more contemporary experience with
better administrative ergonomics. Freecloak seeks to be the glue to hold this
joint together.

## Installation
Freecloak does not currently publish to PyPi as this is an early development
tool. However, it can be installed by cloning the repository and installing
using a local path.

```shell
$ git clone https://github.com/Macr0Nerd/freecloak.git
$ cd freecloak
$ pip install .
$ freecloak --version
freecloak v0.0.0.dev1
```

## Usage
Freecloak is built off of plugins, in fact the core libraries are built off
of the plugin system. When interacting with freecloak on the CLI, you call a
plugin and a command:

```shell
$ freecloak plugins list
Name            Version         Description
=============== =============== ===============
configuration   0.0.0.dev1      keycloak configuration plugin
keycloak        0.0.0.dev1      keycloak interface plugin
logging         0.0.0.dev1      logging and output configuration plugin
plugins         0.0.0.dev1      plugin management plugin
```

## License
    Copyright (C) 2025  Gabriele Ron

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

## Organization
Freecloak OID: 1.3.6.1.4.1.64445
