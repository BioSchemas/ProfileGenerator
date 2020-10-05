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

import rdflib
from string import Template
import logging

_logger = logging.getLogger(__name__)


# https://schema.org/docs/developers.html
SCHEMA_URL=Template("https://schema.org/version/${version}/schemaorg-all-http.jsonld")

def load_schemaorg(schemaver="latest"):
    url = SCHEMA_URL.substitute(version=schemaver)
    _logger.info("Loading %s as RDF Dataset" % url)
    d = rdflib.Dataset()
    result = d.parse(url, format="json-ld")
    _logger.info("Loaded %s quads" % len(d))
    if _logger.isEnabledFor(logging.DEBUG):
        _logger.debug(d.serialize(format="trig").decode("utf-8"))
    return result

def find_properties(schematype, profile, schemaver="latest"):
    load_schemaorg(schemaver)
    return [ # FIXME: hardcoded for now!
        (schematype, []),
        ("CreativeWork", []),
        ("Thing", [{"name": "foo"} ])
    ]