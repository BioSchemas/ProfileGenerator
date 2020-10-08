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
from typing import TypeVar 
from string import Template

import rdflib
from rdflib import Dataset, URIRef
from rdflib.term import Identifier
# rdflib knows about some namespaces, like FOAF
from rdflib.namespace import RDF, RDFS, Namespace

SCHEMA = Namespace("http://schema.org/")

import logging
from ._logging import LOG_TRACE

_logger = logging.getLogger(__name__)

# https://schema.org/docs/developers.html
SCHEMA_URL=Template("https://schema.org/version/${version}/schemaorg-all-http.jsonld")

SchemaType = TypeVar("SchemaType")
SchemaProperty = TypeVar("SchemaProperty")
SchemaClass = TypeVar("SchemaClass")


class SchemaType(type):
    _uri2type = {} 
    _dataset = None
    _graph = None

    def __repr__(self):
        return "<%s>" % self.uri

    def __str__(self):
        return self.label or self.uri

    @classmethod
    def _flush(cls):
        # Always set in SchemaType
        SchemaType._uri2type = {} 
        SchemaType._dataset = None
        SchemaType._graph = None      

    #abstract
    @property
    def label(self):
        return None # Not implemented

    @classmethod
    def dataset(cls, schemaver="latest"):
        if cls._dataset is not None:
            return cls._dataset
        url = SCHEMA_URL.substitute(version=schemaver)
        _logger.info("Loading %s as RDF Dataset" % url)
        d = rdflib.Dataset()
        result = d.parse(url, format="json-ld")
        _logger.info("Loaded %s quads" % len(d))
        if _logger.isEnabledFor(LOG_TRACE):
            _logger.log(LOG_TRACE, d.serialize(format="trig").decode("utf-8"))
        # NOTE: Store it in the submetaclass, e.g. SchemaClass or SchemaProperty
        cls._dataset = d
        return cls._dataset

    @classmethod
    def graph(cls):
        """Find schema.org named graph"""
        if cls._graph is not None:
            return cls._graph
        for (s,p,o,g) in cls.dataset().quads([SCHEMA.Thing,RDF.type,RDFS.Class,None]):
            cls._graph = cls.dataset().graph(g)
        return cls._graph

    @classmethod
    def version(cls):
        return cls.graph().identifier.replace("http://schema.org/#", "")

    @classmethod
    def as_type(cls, uri: URIRef) -> SchemaType:
        if uri not in cls._uri2type:
            # create same subclass (SchemaProperty or SchemaClass)
            cls._uri2type[uri] = cls._new(uri)
        return cls._uri2type[uri]

    @classmethod
    def _new(cls, uri: URIRef) -> SchemaType:
        cls._uri2type[uri] = None # pre-reserve to avoid loops
        _logger.debug("Creating %s for %s" % (cls,uri))
        uri = uri
        bases = tuple(cls._supertypes(uri))
        _logger.debug("..with bases %s" % (bases,))
        C = cls(uri, bases, {"uri": uri})
        cls._uri2type[uri] = C # self-register
        _logger.debug("Mapped %s to %s" % (uri, C))
        return C

    # abstract
    @classmethod
    def _supertypes(cls, uri: URIRef):
        return []

    @property
    def supertypes(self):
        return list(self._supertypes(self.uri))

    @property
    def ancestors(self):
        return [p for p in self.mro() if isinstance(p, SchemaType)]

    @property
    def label(self):
        for label in self.graph().objects(self.uri, RDFS.label):
            return str(label) # usually only one!
        return None

    @property            
    def comment(self):
        for comment in self.graph().objects(self.uri, RDFS.comment):
            return str(comment)
        return None

class SchemaProperty(SchemaType):
    @classmethod    
    def _supertypes(self, uri: URIRef):
        return map(SchemaProperty.as_type, 
            self.graph().objects(uri, RDFS.subPropertyOf))
    
    @property
    def domainIncludes(self) -> SchemaClass:
        return [SchemaClass.as_type(o) for o in
            self.graph().objects(self.uri, SCHEMA.domainIncludes)]
    
    @property
    def rangeIncludes(self) -> SchemaClass:
        return [SchemaClass.as_type(o) for o in 
            self.graph().objects(self.uri, SCHEMA.rangeIncludes)]

class SchemaClass(SchemaType):        
    @classmethod
    def _supertypes(cls, uri: URIRef):
        return map(SchemaClass.as_type, 
            cls.graph().objects(uri, RDFS.subClassOf))

    def includedInDomainOf(self) -> SchemaProperty:
        return [SchemaProperty.as_type(s) for s in
            self.graph().subjects(SCHEMA.domainIncludes, self.uri)]

    def includedInRangeOf(self) -> SchemaProperty:
        return [SchemaProperty.as_type(s) for s in 
            self.graph().subjects(SCHEMA.rangeIncludes, self.uri)]

def find_class(schematype):
    if not isinstance(schematype, Identifier):
        schematype = SCHEMA[schematype]
    return SchemaClass.as_type(schematype)

def find_property(schemaprop):
    if not isinstance(schemaprop, Identifier):
        schemaprop = SCHEMA[schemaprop]
    return SchemaProperty.as_type(schemaprop)

def find_properties(schematype):
    s = find_class(schematype)
    type_properties = OrderedDict()
    for schematype in s.ancestors:
        type_properties[schematype] = list(schematype.includedInDomainOf())
    return type_properties

def get_version():
    return SchemaType.version()

def set_version(version):
    SchemaType._flush()
    SchemaType.dataset(version)
