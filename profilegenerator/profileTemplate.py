#!/usr/bin/env python

# SPDX-License-Identifer: MIT
# Copyright 2020 Heriot-Watt University, UK
# Copyright 2020 The University of Manchester, UK
#

"""
Template for bioschema profile, incl. YAML header
"""

__author__ = "Bioschemas.org community"
__copyright__ = """© 2020 Heriot-Watt University, UK
© 2020 The University of Manchester, UK
"""
__license__ = "MIT" # https://spdx.org/licenses/MIT

import datetime
import urllib.parse
from .profileConstants import *

footerString = ''
ghBase = 'https://github.com/BioSchemas/specifications/'
ghTasksBase = ghBase + 'labels/type%3A%20'
ghExamplesBase = ghBase + 'tree/master/'

def profileHeader(profileName, schemaType, schemaVersion, isBioschemasType, profileDescription, version, status, groupName, hasLiveDeploy):
    header_properties = {}
    header_properties['layout'] = "profile-display"
    header_properties['name'] = profileName
    header_properties['official_type'] = schemaType
    header_properties['schema_version'] = schemaVersion
    if isBioschemasType:
        base_url = BIOSCHEMAS_URL
    else:
        base_url = SCHEMA_URL
    header_properties['type_base_url'] = base_url
    # TODO: Schema version
    header_properties['description'] = profileDescription
    header_properties['version'] = version
    header_properties['version_date'] = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')
    header_properties['status'] = status
    header_properties['spec_type'] = 'Profile'
    header_properties['group'] = groupName
    header_properties['use_cases_url'] = '/useCases/' + profileName + '/'
    header_properties['gh_tasks'] = ghTasksBase + urllib.parse.quote(profileName)
    if hasLiveDeploy:
        header_properties['live_deploy'] = '/liveDeploys/'
    header_properties['full_example'] = ghExamplesBase + profileName + '/examples/' + version
    return header_properties

def profileProperty(propertyName, expectedTypes, schemaDescription, bsDescription, marginality, cardinality, controlledVocabs, example):
    propertyDict = {}
    propertyDict['property'] = propertyName
    propertyDict['expected_types'] = expectedTypes
    propertyDict['description'] = schemaDescription
    propertyDict['type'] = ""
    propertyDict['type_url'] = ""
    propertyDict['bsc_description'] = bsDescription
    propertyDict['marginality'] = marginality
    propertyDict['cardinality'] = cardinality
    propertyDict['controlled_vocab'] = controlledVocabs
    propertyDict['example'] = example
    return propertyDict

def profileType(expectedTypes):
    typesDict = []
    for expected in expectedTypes:
        typeProperties = {}
        typeProperties['type_name'] = str(expected)
        typeProperties['type_base_url'] = SCHEMA_URL
        typesDict.append(typeProperties)
    return typesDict

def profileFooter():
    return(footerString)

if __name__ == "__main__":
    profileName = "Dataset"
    version = '0.3'
    description = '''A guide for how to describe datasets in the life-sciences using Schema.org-like
        annotation.'''
    print(profile(profileName, description, version, 'revision', 'data', True))
