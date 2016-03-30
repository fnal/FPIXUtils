#!/usr/bin/env python
from array import array
import collections
import re
import os

import urllib2
import csv
import json

###############################################################################

# BEGIN PART TRACKING UTILITIES

###############################################################################

###############################################################################

def fancyTable(arrays):

    def areAllEqual(lst):
        return not lst or [lst[0]] * len(lst) == lst

    if not areAllEqual(map(len, arrays)):
        exit('Cannot print a table with unequal array lengths.')

    verticalMaxLengths = [max(value) for value in map(lambda * x:x, *[map(len, a) for a in arrays])]

    spacedLines = []

    for array in arrays:
        spacedLine = ''
        for i, field in enumerate(array):
            diff = verticalMaxLengths[i] - len(field)
            spacedLine += field + ' ' * diff + '\t'
        spacedLines.append(spacedLine)

    return '\n'.join(spacedLines)

###############################################################################

# function to print out the module report table with even columns

def printPartsDictionary(inputFile):

    url = 'http://www.physics.purdue.edu/cmsfpix/Submission_p/tmp/modulereport.csv'
    response = urllib2.urlopen(url)
    reader = csv.reader(response)

    table = []
    isFirstLine = True
    moduleNumber = 1
    for row in reader:
        if isFirstLine:
            nFields = len(row)
            prefix = ['index']
        else:
            prefix = [str(moduleNumber)]
            moduleNumber += 1
        isFirstLine = False
        if len(row) < nFields:
            row.extend(' ' * (nFields - len(row)))
        prefix.extend(row)
        table.append(prefix)

    print fancyTable(table)

###############################################################################

# function to build a python dictionary from a "module report" CSV input
# use module name as key to dictionary

def producePartsDictionary():

    url = 'http://www.physics.purdue.edu/cmsfpix/Submission_p/tmp/modulereport.csv'
    response = urllib2.urlopen(url)
    reader = csv.reader(response)

    dictionary = {}
    headings = []
    isFirstLine = True

    for row in reader:

        if isFirstLine:
            for index in range(1,len(row)):
                headings.append(row[index].strip())
            nFields = len(headings) + 1
            isFirstLine = False
            continue

        if len(row) < nFields:
            row.extend(' ' * (nFields - len(row)))

        moduleName = row[0].strip()
        dictionary[moduleName] = {}
        for index in range(1,len(row)):
            if headings[index-1] == "assembly date":
                entry = row[index].strip()
            else:
                entry = row[index].replace(' ','')
            if not len(entry):
                entry = ' '

            dictionary[moduleName][headings[index-1]] = entry

    return dictionary


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

    return dictionary

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
