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
from typing import TypeVar, List
from string import Template
import sys

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
    _dataset = rdflib.Dataset()
    _graph = rdflib.Dataset()

    def __repr__(self):
        return "<%s>" % self.uri

    def __str__(self):
        return self.label or self.uri

    @classmethod
    def _flush(cls):
        # Always set in SchemaType
        SchemaType._uri2type = {} 
        SchemaType._dataset = rdflib.Dataset()
        SchemaType._graph = rdflib.Graph()      

    #abstract
    @property
    def label(self):
        return None # Not implemented

    @classmethod
    def dataset(cls, schemaver="latest"):
        if cls._dataset:
            return cls._dataset
        url = SCHEMA_URL.substitute(version=schemaver)
        _logger.info("Loading %s as RDF Dataset" % url)
        d = rdflib.Dataset()
        result = d.parse(url, format="json-ld")
        _logger.info("Loaded %s quads" % len(d))
        if _logger.isEnabledFor(LOG_TRACE):
            _logger.log(LOG_TRACE, d.serialize(format="trig").decode("utf-8"))
        # NOTE: Store it in this parent class to support _reset
        SchemaType._dataset = d
        return cls._dataset

    @classmethod
    def graph(cls):
        """Find schema.org named graph"""
        if cls._graph:
            return cls._graph
        for (s,p,o,g) in cls.dataset().quads([SCHEMA.Thing,RDF.type,RDFS.Class,None]):
            # Found the named graph of schema.org declarations
            SchemaType._graph = cls.dataset().graph(g)
        return cls._graph

    @classmethod
    def version(cls):
        return cls.graph().identifier.replace("http://schema.org/#", "")

    @classmethod
    def as_type(cls, uri: URIRef) -> SchemaType:
        if uri not in cls._uri2type:
            if not cls._exists(uri):
                raise ValueError("%s is not a known %s" % (uri, cls))
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

    @classmethod
    def _exists(cls, uri: URIRef) -> bool:
        # Accept any non-schema.org terms like rdf:type
        return not uri.startswith("http://schema.org/")

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
    def _exists(cls, uri: URIRef) -> bool:
        _logger.debug("Checking property %s" % uri)
        return super()._exists(uri) or (uri, RDF.type, RDF.Property) in cls.graph()

    @classmethod    
    def _supertypes(self, uri: URIRef):
        return map(SchemaProperty.as_type, 
            self.graph().objects(uri, RDFS.subPropertyOf))
    
    @property
    def domainIncludes(self):
        return [SchemaClass.as_type(o) for o in
            self.graph().objects(self.uri, SCHEMA.domainIncludes)]

    def domainIncludesWithSuper(self):
        classes = OrderedDict()
        for p in self.ancestors: # use mro order
            for k in p.domainIncludes:
                classes[k] = k
        return list(classes.keys())

    def rangeIncludesWithSuper(self):
        classes = OrderedDict()
        for p in self.ancestors: # use mro order
            for k in p.rangeIncludes:
                classes[k] = k
        return list(classes.keys())

    @property
    def rangeIncludes(self) -> SchemaClass:
        return [SchemaClass.as_type(o) for o in 
            self.graph().objects(self.uri, SCHEMA.rangeIncludes)]

class SchemaClass(SchemaType):
    @classmethod
    def _exists(cls, uri: URIRef) -> bool:
        return super()._exists(uri) or (uri, RDF.type, RDFS.Class) in cls.graph()

    @classmethod
    def _supertypes(cls, uri: URIRef):
        return map(SchemaClass.as_type, 
            cls.graph().objects(uri, RDFS.subClassOf)) 

    @property
    def includedInDomainOf(self):
        a = [SchemaProperty.as_type(s) for s in
            self.graph().subjects(SCHEMA.domainIncludes, self.uri)]
        a.sort(key=str)
        return a

    def includedInDomainOfWithSuper(self):
        props = OrderedDict()
        for k in self.ancestors: # use mro order
            for p in k.includedInDomainOf:
                props[p] = p
        return list(props.keys())

    @property
    def includedInRangeOf(self) -> SchemaProperty:
        return [SchemaProperty.as_type(s) for s in 
            self.graph().subjects(SCHEMA.rangeIncludes, self.uri)]

    def includedInRangeOfWithSuper(self):
        props = OrderedDict()
        for k in self.ancestors: # use mro order
            for p in k.includedInRangeOf:
                props[p] = p
        return list(props.keys())

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
        type_properties[schematype] = schematype.includedInDomainOf
    return type_properties

def get_version():
    return SchemaType.version()

def set_version(version):
    SchemaType._flush()
    SchemaType.dataset(version)


def make_example_value(s_type: SchemaClass, prop: SchemaProperty, 
                 expectedType: SchemaClass) -> str:
    example_id = "https://example.com/%s/123" % str(s_type).lower()
    if not expectedType: 
        exampleValue = '""'
    # Note: We'll only inspect the FIRST type in range
    elif issubclass(expectedType, find_class(SCHEMA.URL)):
        # Some identifier - possibly related to property name
        exampleValue = '"https://purl.example.org/%s-345"' % str(prop).lower()
    elif issubclass(expectedType, find_class(SCHEMA.Person)):
        # Specified type of object
        exampleValue = '{"@id": "https://orcid.org/0000-0002-1825-0097", "@type": "%s"}' % (
            str(expectedType))            
    elif issubclass(expectedType, find_class(SCHEMA.Intangible)):
        # Usually anonymous, e.g. PropertyValue
        exampleValue = '{"@type": "%s"}' % (
            str(expectedType))
    elif issubclass(expectedType, find_class(SCHEMA.Thing)):
        # Specified type of object
        exampleValue = '{"@id": "https://example.com/%s/345", "@type": "%s"}' % (
            str(expectedType).lower(), str(expectedType))            
    elif expectedType.uri == SCHEMA.Thing:
        # Unknown/any type - generic object
        exampleValue = '{"@id": "https://example.org/345"}'
    elif issubclass(expectedType, find_class(SCHEMA.DateTime)):
        exampleValue = '"2020-10-08T17:33:08+01:00"'
    elif issubclass(expectedType, find_class(SCHEMA.Date)):
        exampleValue = '"2020-10-08"'
    elif issubclass(expectedType, find_class(SCHEMA.Time)):
        exampleValue = '"17:33:08"'
    elif issubclass(expectedType, find_class(SCHEMA.Boolean)):
        exampleValue = 'false'
    elif issubclass(expectedType, find_class(SCHEMA.Number)):
        exampleValue = '123'
    elif issubclass(expectedType, find_class(SCHEMA.Text)):
        exampleValue = '"example %s"' % str(prop).lower()
    else:
        # Probably a datatype, fallback to empty string
        exampleValue = '""'
    return exampleValue

def make_example_property(s_type: SchemaClass, prop: SchemaProperty, 
                 expectedType: SchemaClass) -> str:
    example_id = "https://example.com/%s/123" % str(s_type).lower()
    _logger.info("Making example for [a %s] %s [a %s]" % (s_type, prop, expectedType))
    exampleValue = make_example_value(s_type, prop, expectedType)
    ex = '''{ "@context": "https://schema.org/",
  "@id": "%s",
  "@type": "%s",
  "%s": %s
}''' % (example_id, s_type, prop, exampleValue)
    _logger.debug(ex)
    return ex

def _first(iterable):
    for x in iterable:
        return x

def make_example_class(s_type: SchemaClass, properties: List[SchemaProperty]) -> str:
    example_id = "https://example.com/%s/123" % str(s_type).lower()
    _logger.info("Making example for [a %s] *" % s_type)    
    props = ('"%s": %s' % 
        (p, make_example_value(s_type, p, _first(p.rangeIncludesWithSuper())))
        for p in properties)
    ex = '''{ "@context": "https://schema.org/",
  "@id": "%s",
  "@type": "%s",
  %s
}''' % (example_id, s_type, ",\n  ".join(props))
    _logger.debug(ex)
    return ex

def main(args=None):
    """Show example for a particular thing"""
    if not args:
        args = sys.argv[1:]
    if not args or "-h" in args or "--help" in args:
        print("schemaorg-example [TYPE-or-PROPERTY]")
        return
    term = args[0]
    if term[0] == term[0].upper(): # assume is Class
        k = find_class(term)
        ex = make_example_class(k, k.includedInDomainOfWithSuper())
        print(ex)
    else: # assume is property
        p = find_property(term) 
        for d in p.domainIncludesWithSuper():
            for r in p.rangeIncludesWithSuper():
                ex = make_example_property(d,p,r)
                print(ex)
