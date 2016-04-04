#!/usr/bin/env python

import json

from testResultsTrackingTools import *
from componentTrackingTools import *

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--force", action="store_true", dest="force", default=False,
                  help="force reprocessing of all modules")
(arguments, args) = parser.parse_args()

partsDictionary = producePartsDictionary()
modules = [module for module in partsDictionary]

gradeDictionary = produceGradeDictionary(modules, arguments.force)

with open('moduleGrades.json', 'w') as outputFile:
    json.dump(gradeDictionary, outputFile, sort_keys=True, indent=4)

