#!/usr/bin/env python
from array import array
import collections
import re
import os

import urllib2
import csv
import json

import pandas as pd

###############################################################################

# BEGIN PART TRACKING UTILITIES

###############################################################################

###############################################################################

# function to build a pandas dataframe from a "module report" CSV input
# use module name as key to dictionary

def producePartsDictionary():

    url = 'http://www.physics.purdue.edu/cmsfpix/Submission_p/tmp/modulereport.csv'
    df = pd.read_csv(url, index_col="module", skipinitialspace=True)
    # delete final empty column
    df.drop(df.columns[[-1]], axis=1, inplace=True)
    return df

###############################################################################

# function to build a pandas dataframe from a "module report" CSV input
# use sensor-based module name as key to dictionary

def produceRTIPartsDictionary():

    indices = [
        'TT',
        'FL',
        'LL',
        'CL',
        'CR',
        'RR',
        'FR',
        'BB']

    def getFinalSensorName(row):
        module = "WL_"
        position = indices[int(row["Module #"])-1]
        module += position + "_"
        wafer = row["Sensor Wafer"].strip()
        letter = wafer[0]
        index = ord(letter) - ord('B')
        new_wafer = str(index) + '0'*(3-len(wafer)) + wafer[1:]
        module += new_wafer
        return module

    def getFullROCAddress(wafer, roc):
        prefix = wafer.split("(")[0]
        return prefix + "-" + roc

    df = pd.read_csv("RTI_spreadsheet.csv")#, index_col="module", skipinitialspace=True)
    # Remove rows with missing data
    df = df[ ~pd.isnull(df["Sensor Wafer"]) ]

    # include final sensor name
    df.loc[:,"sensor"] = df.apply(lambda row: getFinalSensorName(row), axis=1)
    df.set_index("sensor", drop=True, inplace=True)

    for roc in range(16):
        df.loc[:,"ROC" + str(roc)] = df.apply(lambda row: getFullROCAddress(row['ROC'+str(roc+1)+'Wfr'],row['ROC'+str(roc+1)]), axis=1)

    # get rid of unnecessary columns
    df = df.drop('Sensor Wafer', 1)
    df = df.drop('Module #', 1)
    df = df.drop('ROC16', 1)
    df = df.drop('Comments', 1)
    df = df.drop('Unnamed: 0', 1)
    good_cols = [col for col in df.columns if "Wfr" not in col]
    df = df[good_cols]
#    print df

    return df

###############################################################################

# function to build a pandas dataframe from a ROC wafer testing output file
# use wafer position, e.g. "63A" as key

def produceROCGradeDictionary(wafer):
    inputFile = "/Users/lantonel/FPIXUtils/databaseTools/ROCTestingResults/" + wafer + ".json"

    dictionary = {}

    if not os.path.exists(inputFile):
        print inputFile, "not found, skipping..."
        return pd.DataFrame()
    with open(inputFile) as data_file:
        for line in data_file:
            if len(line) < 100:
                continue
            data = json.loads(line)
            dictionary[data['ROC_ID']] = data['RESULT']

    df = pd.DataFrame(dictionary.items(),columns=['ROC ID', 'Grade'])
    return df

###############################################################################

# function to build a python dictionary from the sensor wafer testing output file
# use wafer number, e.g. "153" as key

def produceSensorGradeDictionary(inputFile):

    dictionary = {}

    if not os.path.exists(inputFile):
        print inputFile, "not found, skipping..."
        return dictionary
    with open(inputFile) as data_file:
        for line in data_file:
            splitline = line.split()
            wafer = splitline[0]
            dictionary[wafer] = []
            for position in range(1,len(splitline)):
                dictionary[wafer].append(int(splitline[position]))

    return dictionary


###############################################################################

# function to return a dictionary of the wafer coordinates of a ROC
# takes the partsDictionary, module name, and chip index as input

def getROCCoordinates(partsDictionary, moduleName, chipIndex):
    errorCode = ["?","?","?","?"]
    if moduleName not in partsDictionary.index:
        return errorCode
    entry = partsDictionary.loc[moduleName]["ROC"+str(chipIndex)].rstrip()
    if len(entry) < 4:
        return errorCode

    wafer = entry.split("-")[0]
    x_index = entry[-3]
    y_index = entry[-2]
    reticle_index = entry[-1]

    return [wafer, x_index, y_index, reticle_index]

###############################################################################

# function to return the sensor wafer and position of the specified module
# takes the partsDictionary and module name as input

def getSensorCoordinates(partsDictionary, moduleName):
    errorCode = ["?","?"]
    if moduleName not in partsDictionary.index:
        return errorCode
    entry = partsDictionary.loc[moduleName]["sensor"].split("_")
    if len(entry) < 3:
        return errorCode
    wafer = entry[2]
    position = entry[1]

    return [wafer, position]

###############################################################################

# function to print ROC information for a given module

def printROCCoordinates(partsDictionary, moduleName):

    print
    print "module: " + moduleName
    print "wafer: " + getROCCoordinates(partsDictionary, moduleName, 0)[0]
    print "chips:",
    for chipIndex in range(16):
        rocCoordinates = getROCCoordinates(partsDictionary, moduleName, chipIndex)
        location = rocCoordinates[1] + rocCoordinates[2] + rocCoordinates[3]
        print location,
    print

###############################################################################

# returns list of all ROC wafers used in production

def getListOfROCWafers(partsDictionary):

    listOfWafers = []

    for moduleName in partsDictionary.index:
        for chipIndex in range(16):
            wafer = getROCCoordinates(partsDictionary, moduleName, chipIndex)[0]

            if wafer != "?" and wafer not in listOfWafers:
                listOfWafers.append(wafer)

    return listOfWafers

###############################################################################

# returns list of all Sensor wafers used in production

def getListOfSensorWafers(partsDictionary):

    listOfWafers = []

#    print partsDictionary

    modules = partsDictionary.index.unique().tolist()

    for moduleName in modules:
        for chipIndex in range(16):
            wafer = getSensorCoordinates(partsDictionary, moduleName)[0]

            if wafer != "?" and wafer not in listOfWafers:
                listOfWafers.append(wafer)

    return listOfWafers
