#!/usr/bin/env python

import json

from testResultsTrackingTools import *
from componentTrackingTools import *

partsDictionary = producePartsDictionary()
modules = [module for module in partsDictionary]

gradeDictionary = produceGradeDictionary(modules)

with open('moduleGrades.json', 'w') as outputFile:
    json.dump(gradeDictionary, outputFile, sort_keys=True, indent=4)

