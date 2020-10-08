#!/usr/bin/env python

# SPDX-License-Identifer: MIT
# Copyright 2020 Heriot-Watt University, UK
# Copyright 2020 The University of Manchester, UK
#


"""
Custom log levels
"""

__author__ = "Bioschemas.org community"
__copyright__ = """© 2020 Heriot-Watt University, UK
© 2020 The University of Manchester, UK
"""
__license__ = "MIT" # https://spdx.org/licenses/MIT

import logging

LOG_TRACE = int(logging.DEBUG / 2) # 5
LOG_ANNOUNCE = logging.WARNING + 1 # 31
logging.addLevelName(LOG_TRACE, "TRACE")
logging.addLevelName(LOG_ANNOUNCE, "ANNOUNCE")