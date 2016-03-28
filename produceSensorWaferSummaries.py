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

# compile list of all Sensor wafers used
listOfWafers = getListOfSensorWafers(partsDictionary)

# use the Sensor wafer as the key
plotDictionary = {}
for wafer in listOfWafers:
    # each wafer contains a list of histograms and locations
    plotDictionary[wafer] = []

counter = 1
for name in glob.glob(resultsDirectory + 'M*.root'):
    moduleName = name.split("/")[5].split("_")[0]

    print "module #" + str(counter) + ": " +  moduleName
    counter += 1

    sensorCoordinates = getSensorCoordinates(partsDictionary, moduleName)
    wafer = sensorCoordinates[0]
    position = sensorCoordinates[1]
    if wafer == "?":
        continue

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

    summaryPlot = makeMergedPlot(plots)
    summaryPlot.SetName(moduleName)
    info = {'position' : position, 'plot' : summaryPlot}
    plotDictionary[wafer].append(info)

for wafer in listOfWafers:
    if len(plotDictionary[wafer]):
        saveSensorWaferCanvas(wafer, inputPath, plotDictionary, -5, 5)
