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
from ._logging import LOG_TRACE, LOG_ANNOUNCE
from .schemaorg import SCHEMA, SchemaProperty, SchemaClass
from . import schemaorg
from .profileTemplate import profileHeader, profileProperty, profileType, profileFooter
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


def _str_presenter(dumper, data):
    if "\n" in data:
        style='|'
    elif len(data) > 76:
        style='>'
    elif '"' in data or ' ' in data or ":" in data:
        style='"'
    elif "'" in data:
        style="'"
    else:
        style=''
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)
yaml.add_representer(str, _str_presenter)

##

## https://stackoverflow.com/a/41786451
# CC BY-SA 4.0 by Jace Browning & Anthon
def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')
yaml.add_representer(type(None), represent_none)
##



def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Generate Bioschemas.org profile template for a given schema.org type')

    # Common options
    parser.add_argument("schematype", metavar="TYPE",
        help='schema.org type, e.g. "Dataset"')
    parser.add_argument("profile", metavar="PROFILE", nargs="?",
        help='bioschema.org profile name, e.g. "Dataset" (default: same as TYPE)',
        default=None)

    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    parser.add_argument('--force', '-f', action="store_true",
        help="Do not ask before overwriting profile output file")

    parser.add_argument('--output', '-o', metavar="OUTPUT", default=None,
        help="Set profile output file, or `-` for stdout (default: PROFILE-0.1-DRAFT.html)")

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



def generate(schematype, profileName=None, groupName=None, description=None, filename=None, overwrite=False):
    """Generate bioschemas profile for a given schematype"""
    assert schematype
    profileName = profileName or schematype
    groupName = groupName or profileName    
    

    typ = schemaorg.find_class(schematype)
    props = schemaorg.find_properties(schematype)
    
    ## TODO: Make yaml, template etc.
    _logger.info("Profile: %s" % profileName)
    schemaver = schemaorg.get_version()
    _logger.info("Based on schema.org %s version %s" % (typ, schemaver))
    mappingProperies = []
    for (s_type, s_props) in props.items():
        _logger.debug("Type: %s " % s_type)
        _logger.debug("Properties: %s", s_props)        
        for prop in s_props:
            propertyName = str(prop)
            expectedTypes = profileType(prop.rangeIncludes)
            schemaDescription = prop.comment or prop.label or str(prop)
            bsDescription = 'TODO: Bioschemas description'
            marginality = MARGINALITY_UNSPECIFIED
            cardinality = ""
            controlledVocabs = ""
            example = schemaorg.make_example_property(typ, prop, 
                prop.rangeIncludes and prop.rangeIncludes[0])
            # TODO: record which s_type this property belongs to
            mappingProperies.append(profileProperty(propertyName, expectedTypes, schemaDescription, 
                bsDescription, marginality, cardinality, controlledVocabs, example))

    superclasses = typ.ancestors
    superclasses.reverse()
    description = description or typ.comment or profileName 
    version = "0.1"
    status = STATUS_DRAFT
    profile = '---\n'
    profileDict = profileHeader(profileName, schematype, schemaver, False, description, version, status, groupName, False)
    profileDict['hierarchy'] = profileType(superclasses)
    profileDict['mapping'] = mappingProperies
    profile += yaml.dump(profileDict, default_flow_style=False, default_style='"', sort_keys=False)
    profile += '---\n'
    profile += profileFooter()
    writeToFile(profileName, version, status, profile, filename, overwrite)
    # print(profile)

def writeToFile(profileName, version, status, profile, filename, overwrite):
    if not filename:
        filename = profileName+'-'+version+'-'+status+'.html'
    if (os.path.exists(filename) and not overwrite):
        _logger.warning("File already exists: %s" % os.path.abspath(filename))
        while 1:
            question = 'Overwrite '+ filename + ' (Y/n): '
            sys.stderr.write(question)
            choice = input().lower()
            if choice[:1] == 'y' or choice[:1] == '':
                break
            elif choice[:1] == 'n':
                _logger.fatal("File %s already exists and not overwritten." % filename)
                return
            else:
                sys.stderr.write("Please respond with 'y' or 'n'.\n")
    if filename == "-":
        fo = sys.stdout
    else:
        fo = open(filename, 'w')
    fo.write(profile)
    fo.close()
    _logger.log(LOG_ANNOUNCE, "Generated %s" % os.path.abspath(filename))

# LOG_ANNOUNCE is above logging.WARNING and always showed
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
        schemaorg.set_version(args.schemaver)
        return generate(schematype, profileName, groupName, args.description, args.output, args.force)
    except OSError as e:
        _logger.fatal(e)
        return Status.IO_ERROR

