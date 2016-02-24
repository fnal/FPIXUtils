#!/usr/bin/env python                                                                                                                                                                                     
from componentTrackingTools import *
from moduleSummaryPlottingTools import *
import sys
import glob

gROOT.SetBatch()

moduleReportFile = '/Users/lantonel/FPIXUtils/modulereport.csv'
resultsDirectory = '/Users/lantonel/PlotsAndTables/ModuleTestResults/'

# parse list of module components
partsDictionary = producePartsDictionary(moduleReportFile)

# compile list of all ROC wafers used
listOfWafers = getListOfROCWafers(partsDictionary)

# use the ROC wafer as the key
plotDictionary = {}
for wafer in listOfWafers:
    # each wafer contains a list of histograms and locations
    plotDictionary[wafer] = []


for name in glob.glob(resultsDirectory + 'M*.root'):
    moduleName = name.split("/")[5].split("_")[0]

# choose histogram to use for summary plot
#    inputPath = 'Scurves/sig_scurveVcal_Vcal'
    inputPath = 'BB3/rescaledThr'
#    inputPath = 'PixelAlive/PixelAlive'

    plots = produce2DPlotList(name, inputPath)
    if plots is None:
        continue

# convert input to binary plots if desired
#    makeBinaryPlots(plots,-0.1,0.1)
#    makeBinaryPlots(plots,5,-5)


    for chipIndex in range(16):
        rocCoordinates = getROCCoordinates(partsDictionary, moduleName, chipIndex)
        wafer = rocCoordinates[0]
        if wafer == "?":
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
        saveROCWaferCanvas(wafer, inputPath, plotDictionary, 0, 1)
