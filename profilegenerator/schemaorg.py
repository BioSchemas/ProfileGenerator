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

def find_properties(schematype, profile):
    return [ # FIXME: hardcoded for now!
        (schematype, []),
        ("CreativeWork", []),
        ("Thing", [{"name": "foo"} ])
    ]