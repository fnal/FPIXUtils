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

# function to build a python dictionary from a "module report" CSV input
# use module name as key to dictionary

def producePartsDictionary():

    url = 'http://www.physics.purdue.edu/cmsfpix/Submission_p/tmp/modulereport.csv'
    df = pd.read_csv(url, index_col="module", skipinitialspace=True)
    # delete final empty column
    df.drop(df.columns[[-1]], axis=1, inplace=True)
    return df

###############################################################################

# function to build a python dictionary from a ROC wafer testing output file
# use wafer position, e.g. "63A" as key

def produceROCGradeDictionary(wafer):
    inputFile = "/Users/lantonel/FPIXUtils/ROCTestingResults/" + wafer + ".json"

    dictionary = {}

    if not os.path.exists(inputFile):
        print inputFile, "not found, skipping..."
        return dictionary
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
    if moduleName not in partsDictionary:
        return errorCode
    entry = partsDictionary[moduleName]["ROC"+str(chipIndex)]
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
    if moduleName not in partsDictionary:
        return errorCode
    entry = partsDictionary[moduleName]["sensor"].split("_")
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

    for moduleName in partsDictionary:
        if "module" in moduleName:
            print moduleName, getROCCoordinates(partsDictionary, moduleName, 0)
        for chipIndex in range(16):
            wafer = getROCCoordinates(partsDictionary, moduleName, chipIndex)[0]

            if wafer != "?" and wafer not in listOfWafers:
                listOfWafers.append(wafer)

    return listOfWafers

###############################################################################

# returns list of all Sensor wafers used in production

def getListOfSensorWafers(partsDictionary):

    listOfWafers = []

    for moduleName in partsDictionary:
        for chipIndex in range(16):
            wafer = getSensorCoordinates(partsDictionary, moduleName)[0]

            if wafer != "?" and wafer not in listOfWafers:
                listOfWafers.append(wafer)

    return listOfWafers
