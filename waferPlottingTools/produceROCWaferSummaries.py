#!/usr/bin/env python
from databaseTools.componentTrackingTools import *
from waferPlottingTools import *
import sys
import glob

gROOT.SetBatch()

resultsDirectory = '/Users/lantonel/PlotsAndTables/UniqueTestResults/'

# parse list of module components
partsDictionary = producePartsDictionary()

# compile list of all ROC wafers used
listOfWafers = getListOfROCWafers(partsDictionary)

# use the ROC wafer as the key
plotDictionary = {}
for wafer in listOfWafers:
    # each wafer contains a list of histograms and locations
    plotDictionary[wafer] = []

counter = 1
listOfDirs = glob.glob(resultsDirectory + '/M*/*/commander*.root')
for name in listOfDirs:
    moduleName = name.split("/")[-3].split("_")[0]

#    if moduleName != 'M-Y-T-NP':
#        continue

    print "module #" + str(counter) + ": " +  moduleName
    counter += 1


# choose histogram to use for summary plot
#    inputPath = 'Scurves/sig_scurveVcal_Vcal'
    inputPath = 'BB3/rescaledThr'
#    inputPath = 'PixelAlive/PixelAlive'

    plots = produce2DPlotList(name, inputPath)
    if plots is None:
        print "no valid plots"
        continue

# convert input to binary plots if desired
#    makeBinaryPlots(plots,-0.1,0.1)
#    makeBinaryPlots(plots,5,-50)

    for chipIndex in range(16):
        rocCoordinates = getROCCoordinates(partsDictionary, moduleName, chipIndex)
        wafer = rocCoordinates[0]
        if wafer == "?":
            print "no wafer found, skipping"
            continue
        pad = int(rocCoordinates[1]) * 10 + int(rocCoordinates[2]) + 1
        subpad = ord(rocCoordinates[3]) - ord('A') + 1
        plot = plots[chipIndex].Clone()
        plot.SetTitle(inputPath)
        plot.SetStats(False)
        plot.SetName(wafer + "_" + rocCoordinates[1] + rocCoordinates[2] + rocCoordinates[3])
        info = {'pad' : pad, 'subpad' : subpad, 'plot' : plot}
        plotDictionary[wafer].append(info)

for wafer in listOfWafers:
    if len(plotDictionary[wafer]):
        saveROCWaferCanvas(wafer, inputPath, plotDictionary, -5, 5)
#        saveROCWaferCanvas(wafer, inputPath, plotDictionary, 0, 1)
