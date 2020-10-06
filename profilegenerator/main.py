#!/usr/bin/env python

# SPDX-License-Identifer: MIT
# Copyright 2020 Heriot-Watt University, UK
# Copyright 2020 The University of Manchester, UK
#


"""
Bioschemas profile generator
"""

__author__ = "Bioschemas.org community"
__copyright__ = """© 2020 Heriot-Watt University, UK
© 2020 The University of Manchester, UK
"""
__license__ = "MIT" # https://spdx.org/licenses/MIT

import sys
import errno
import logging
import argparse
from enum import IntEnum

from ._version import __version__
from ._logging import LOG_TRACE
from .schemaorg import find_properties
from .profileTemplate import profileHeader, profileProperty, profileFooter

import yaml

_logger = logging.getLogger(__name__)

class Status(IntEnum):
    """Exit codes from main()"""
    OK = 0
    UNHANDLED_ERROR = errno.EPERM
    UNKNOWN_TYPE = errno.EINVAL
    IO_ERROR = errno.EIO
    TYPE_NOT_FOUND = errno.ENOENT
    NOT_A_DIRECTORY = errno.ENOTDIR
    PERMISSION_ERROR = errno.EACCES
    NOT_IMPLEMENTED = errno.ENOSYS
    # User-specified exit codes
    # http://www.tldp.org/LDP/abs/html/exitcodes.html
    OTHER_ERROR = 166


def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Generate Bioschemas.org profile template for a given schema.org type')

    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    parser.add_argument('-v', '--verbose', action='count', default=0,
        help='Increase verbosity level. Repeat -v for debug and trace logs')

    # Common options
    parser.add_argument("schematype", metavar="TYPE",
        help="schema.org type, e.g. Dataset"
        )
    parser.add_argument("profile", metavar="PROFILE", nargs="?",
        help="bioschema.org profile name, e.g. Dataset (by default same as TYPE)",
        default=None
    )
    parser.add_argument("--schemaver", "-s", metavar="VERSION",
        help="schema.org version to fetch, e.g. 10.0 (default: latest)",
        default="latest")
    return parser.parse_args(args)

def generate(schematype, profileName=None, schemaver="latest"):
    """Generate bioschemas profile for a given schematype"""
    profileName = profileName or schematype
    props = find_properties(schematype, profileName, schemaver)

    ## TODO: Make yaml, template etc.
    _logger.info("Profile: %s" % profileName)
    _logger.info("Based on schema.org: %s" % schemaver)
    for (typ, properties) in props:
        _logger.debug("Type: %s " % typ)
        _logger.debug("Properties:")
        for prop in properties:
            _logger.debug("%s" % prop)
    profile = '---\n'
    profileDict = profileHeader(profileName, profileName, "0.1-DRAFT", "draft", profileName, False)
    mappingProperies = []
    mappingProperies.append(profileProperty('schemaPropertyName', '- type 1\n - type 2', 'schema property description', 'Bioschemas description', 'unspecified', None, None, None))
    profileDict['mapping'] = mappingProperies
    profile += yaml.dump(profileDict)
    profile += '---\n'
    profile += profileFooter()
    print(profile)


LOG_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG, LOG_TRACE]

def main(args=None):
    """Main method"""
    try:
        args = parse_args(args)
        # Count of -v -v to set logging
        logging.basicConfig(level=LOG_LEVELS[min(len(LOG_LEVELS)-1, args.verbose)])

        schematype = args.schematype
        assert schematype
        if "profile" in args:
            profileName = args.profile
        else:
            profileName = schematype
        return generate(schematype, profileName, args.schemaver)
    except OSError as e:
        _logger.fatal(e)
        return Status.IO_ERROR
