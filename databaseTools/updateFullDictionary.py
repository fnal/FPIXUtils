#!/usr/bin/env python

import json
import pandas as pd

from testResultsTrackingTools import *
from componentTrackingTools import *

partsDictionary = producePartsDictionary()
gradeDictionary = pd.read_json("moduleGrades.json", orient='index')

fullDictionary = partsDictionary.join(gradeDictionary)

fullDictionary.to_json("moduleInfo.json",orient='index')

print fullDictionary.groupby(['Lessweb Grade']).get_group('A')
