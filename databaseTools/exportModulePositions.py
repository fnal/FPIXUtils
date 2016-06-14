#!/usr/bin/env python

import json
import pandas as pd

from moduleTrackingTools import *

df = produceModuleDictionary()
df_slice = df[~pd.isnull(df['Position'])]
df_slice = df_slice[['Position']]

df_slice.to_csv('ModulePositions.csv')

