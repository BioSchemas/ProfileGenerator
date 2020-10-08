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
    """
    Generates the YAML for the header section of the profile.

    Parameters
    ----------
    profileName : str
        Name of the profile
    schemaType : str
        Name of the Schema.org type over which the profile is defined
    schemaVersion : str
        Version number of Schema.org vocabulary used
    isBioschemasType : bool
        Whether we are defining a new type in the Bioschemas namespace
    profileDescription : str
        Description string for the type
    version : str
        Version number of the profile
    status : str
        Status of the profile which takes a constant of STATUS_DRAFT, STATUS_RELEASE, STATUS_DEPRECATED
    groupName : str
        The identifying name of the Bioschemas Working Group
    hasLiveDeploy : bool
        Indicates whether there are live deployments available for the profile

    RETURNS
    -------
    dict
        Dictionary of terms used for profile YAML display on website
    """

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
    """
    Generates the YAML for a property in the profile.

    Parameters
    ----------
    propertyName : str
        Name of the property
    expectedTypes : str[]
        String array of the types that are the range of the property
    schemaDescription : str
        The schema.org description of the property
    bsDescription : str
        The Bioschemas refinement of the description of the property
    marginality : str
        The marginality level of the property. It can take one of the following
        values: MARGINALITY_MINIMAL, MARGINALITY_RECOMMEDED,
        MARGINALITY_OPTIONAL, MARGINALITY_NOT_APPLICABLE, MARGINALITY_UNSPECIFIED
    cardinality : str
        The cardinality of the property. It can take one of the following
        values: CARDINALITY_ONE, CARDINALITY_MANY
    controlledVocabs : str
        The ontology/ontologies from which Bioschemas recommends the objects of
        this property are drawn.
    example : str
        The example usage of this property. This should be in valid JSON-LD,
        although it is not necessary to repeat the `@context`, `@type`, etc

    RETURNS
    -------
    dict
        Dictionary of terms used for the property in the website YAML
    """
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
