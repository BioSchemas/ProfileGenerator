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

from ._version import __version__
from .schemaorg import find_properties

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

    # Common options
    parser.add_argument("schematype", metavar="TYPE",
        help="schema.org type, e.g. Dataset"
        )
    parser.add_argument("profile", metavar="PROFILE",
        help="bioschema.org profile name, e.g. Dataset (by default same as TYPE)",
        default=None
        )
    return parser.parse_args(args)

def generate(schematype, profile):
    """Generate bioschemas profile for a given schematype"""
    props = find_properties(schematype)
    
    ## TODO: Make yaml, template etc.
    print("Profile: %s" % profile)
    for (typ, properties) in props:
        print("Type: %s " % typ)
        print("Properties:")
        for prop in properties:
            print("%s" % prop)

def main(args=None):
    """Main method"""
    try:
        args = parse_args(args)
        schematype = args.schematype
        assert schematype
        if args.profile:
            profile = args.profile
        else:
            profile = schematype
        return generate(schematype, profile)
    except OSError as e:
        _logger.fatal(e)
        return Status.IO_ERROR
