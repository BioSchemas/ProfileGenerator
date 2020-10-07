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
from .profileConstants import *

import yaml
import os

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

    # Common options
    parser.add_argument("schematype", metavar="TYPE",
        help='schema.org type, e.g. "Dataset"')
    parser.add_argument("profile", metavar="PROFILE", nargs="?",
        help='bioschema.org profile name, e.g. "Dataset" (default: same as TYPE)',
        default=None)

    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    parser.add_argument('-v', '--verbose', action='count', default=0,
        help='Increase verbosity level. Repeat -v for debug and trace logs')

    parser.add_argument("--group", "-g", metavar="GROUP",
        help='bioschema.org profile name, e.g. "Workflow" (default: same as PROFILE)',
        default=None)    
    parser.add_argument("--description", "-d", metavar="DESCRIPTION",
        help="bioschema.org profile description (default: TYPE's schema.org description)",
        default=None)
    parser.add_argument("--schemaver", "-s", metavar="VERSION",
        help='schema.org version to fetch, e.g. 10.0 (default: "latest")',
        default="latest")
    return parser.parse_args(args)

def generate(schematype, profileName=None, schemaver="latest", groupName=None, description=None):
    """Generate bioschemas profile for a given schematype"""
    assert schematype and schemaver
    profileName = profileName or schematype
    groupName = groupName or profileName
    
    props = find_properties(schematype, profileName, schemaver)
    
    ## TODO: Make yaml, template etc.
    _logger.info("Profile: %s" % profileName)
    _logger.info("Based on schema.org: %s" % schemaver)
    for (typ, properties) in props:
        _logger.debug("Type: %s " % typ)
        _logger.debug("Properties:")
        for prop in properties:
            _logger.debug("%s" % prop)
    description = description or profileName ## TODO: From type
    # TODO: Schema version
    # TODO: Type hierarchy as dict with namespace and typename
    version = "0.1"
    status = STATUS_DRAFT
    profile = '---\n'
    profileDict = profileHeader(profileName, schematype, schemaver, False, description, version, status, groupName, False)
    mappingProperies = []
    # TODO: Include mapping of property to domain ontology terms
    mappingProperies.append(profileProperty('schemaPropertyName', ['type 1','type 2'], 'schema property description', 'Bioschemas description', MARGINALITY_UNSPECIFIED, None, None, None))
    profileDict['mapping'] = mappingProperies
    profile += yaml.dump(profileDict)
    profile += '---\n'
    profile += profileFooter()
    writeToFile(profileName, version, status, profile)
    print(profile)

def writeToFile(profileName, version, status, profile):
    filename = profileName+'-'+version+'-'+status+'.html'
    if (os.path.exists(filename)):
        _logger.warning("File already exists: %s" % filename)
        while 1:
            question = 'Overwrite '+ filename + ' (Y/n): '
            sys.stdout.write(question)
            choice = input().lower()
            if choice[:1] == 'y' or choice[:1] == '':
                break
            elif choice[:1] == 'n':
                _logger.fatal("File %s already exists and not overwritten." % filename)
                return
            else:
                sys.stdout.write("Please respond with 'y' or 'n'.\n")
    fo = open(filename, 'w')
    fo.write(profile)
    fo.close()

LOG_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG, LOG_TRACE]

def main(args=None):
    """Main method"""
    try:
        args = parse_args()
        # Count of -v -v to set logging
        logging.basicConfig(level=LOG_LEVELS[min(len(LOG_LEVELS)-1, args.verbose)])

        schematype = args.schematype
        assert schematype
        profileName = "profile" in args and args.profile or schematype
        groupName = args.group or profileName        
        return generate(schematype, profileName, args.schemaver, groupName, args.description)
    except OSError as e:
        _logger.fatal(e)
        return Status.IO_ERROR
