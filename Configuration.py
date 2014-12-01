#!/usr/bin/env python
#
# Stores all of the configuration options in a grammar file as
# key/value pairs.

import json
import sys

#------------------------------------------------------------------------------
#     ____             __ _                       _   _             
#    / ___|___  _ __  / _(_) __ _ _   _ _ __ __ _| |_(_) ___  _ __  
#   | |   / _ \| '_ \| |_| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \ 
#   | |__| (_) | | | |  _| | (_| | |_| | | | (_| | |_| | (_) | | | |
#    \____\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|
#                           |___/                                   
class Configuration(object):

    def __init__(self):
        self.options = {} # empty hash of configuration options


    def __str__(self):
        """Returns a JSON string representation of the configuration."""
        return json.dumps(self.options)

    def add(self, key, value):
        """Adds a new <key,value> pair to the configuration."""
        self.options[key] = value