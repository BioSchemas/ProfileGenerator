#!/usr/bin/env python

# SPDX-License-Identifer: MIT
# Copyright 2020 Heriot-Watt University, UK
# Copyright 2020 The University of Manchester, UK
#

"""
schema.org parser
"""

__author__ = "Bioschemas.org community"
__copyright__ = """© 2020 Heriot-Watt University, UK
© 2020 The University of Manchester, UK
"""
__license__ = "MIT" # https://spdx.org/licenses/MIT

from collections import OrderedDict

import rdflib
from rdflib import Dataset, URIRef
# rdflib knows about some namespaces, like FOAF
from rdflib.namespace import RDF, RDFS, Namespace
SCHEMA = Namespace("http://schema.org/")

from string import Template
import logging
from ._logging import LOG_TRACE

_logger = logging.getLogger(__name__)

# https://schema.org/docs/developers.html
SCHEMA_URL=Template("https://schema.org/version/${version}/schemaorg-all-http.jsonld")

def load_schemaorg(schemaver="latest"):
    url = SCHEMA_URL.substitute(version=schemaver)
    _logger.info("Loading %s as RDF Dataset" % url)
    d = rdflib.Dataset()
    result = d.parse(url, format="json-ld")
    _logger.info("Loaded %s quads" % len(d))
    if _logger.isEnabledFor(LOG_TRACE):
        _logger.log(LOG_TRACE, d.serialize(format="trig").decode("utf-8"))
    return result

class SchemaType(Type):
    _uri2type = {}

    @classmethod
    def _as_type(cls, uri: URIRef) -> SchemaType:
        if uri not in cls._uri2type:
            # create same subclass (SchemaProperty or SchemaClass)
            cls._uri2type[uri] = cls(uri, cls.dataset)
        return cls._uri2type[uri]
    
    def __init__(self, uri: URIRef, dataset: Dataset)
        self.uri = uri
        self.dataset = dataset
        self._uri2type[uri] = self # self-register
        bases = list(cls.supertypes())
        super().__init__(uri, bases, {})

    # abstract
    def supertypes(self):
        return []
    def label(self):
        for label in self.dataset.objects(self.uri, RDFS.label):
            return label
    def comment(self):
        for comment in self.dataset.objects(self.uri, RDFS.comment):
            return comment

class SchemaProperty(SchemaType):
    def supertypes(self):
        return self.dataset.objects(self.uri, RDFS.subPropertyOf)
    
    def domainIncludes(self):
        return map(SchemaClass._as_type, 
            self.dataset.objects(self.uri, RDFS.domainIncludes))        
    
    def rangeIncludes(self):
        return map(SchemaClass._as_type, 
            self.dataset.objects(self.uri, RDFS.rangeIncludes))        

class SchemaClass(Type):
    def supertypes(self):
        return map(SchemaClass._as_type, 
            self.dataset.objects(self.uri, RDFS.subClassOf))

    def propertiesIncludingAsDomain(self):
        return map(SchemaProperty._as_type, 
            self.dataset.subjects(self.uri, SCHEMA.domainIncludes))

    def propertiesIncludingAsRange(self):
        return map(SchemaProperty._as_type, 
            self.dataset.subjects(self.uri, SCHEMA.rangeIncludes))

def find_properties(schematype, schemaver="latest"):    
    s = SchemaType(SCHEMA[schematype], load_schemaorg(schemaver))
    type_properties = OrderedDict()
    for schematype in s.mro():
        type_properties[schematype] = schematype.propertiesIncludingAsDomain()
    return type_properties

