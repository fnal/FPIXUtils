#!/usr/bin/env python

import json
import pandas as pd

from moduleTrackingTools import *
from componentTrackingTools import *

# produce parts dataframe
partsDictionary = producePartsDictionary()

# parse DB module report containing dates and grades
lesswebDictionary = produceModuleDictionary()

# parse MoReWeb grades and their test dates
morewebDictionary = scrapeMoReWeb()

# join moreweb and lessweb dataframes
gradeDictionary = morewebDictionary.join(lesswebDictionary, how = 'outer')

# join parts and module dataframes
fullDictionary = partsDictionary.join(gradeDictionary, how = 'outer')

# convert back to python dictionary for prettier json output
dictionary = fullDictionary.to_dict(orient='index')
with open('moduleInfo.json', 'w') as outputFile:
    json.dump(dictionary, outputFile, sort_keys=True, indent=4)
