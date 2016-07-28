#!/usr/bin/env python                                                                                                                                                                                     
from databaseTools.componentTrackingTools import *
from moduleSummaryPlottingTools import *
from waferPlottingTools import *
import sys
import glob

gROOT.SetBatch()

#resultsDirectory = '/Users/lantonel/PlotsAndTables/PurdueResults/'
resultsDirectory = '/Users/lantonel/PlotsAndTables/UniqueTestResults/'

# parse list of module components
partsDictionary = producePartsDictionary()

# compile list of all Sensor wafers used
listOfWafers = getListOfSensorWafers(partsDictionary)


# use the Sensor wafer as the key
plotDictionary = {}
for wafer in listOfWafers:
    # each wafer contains a list of histograms and locations
    plotDictionary[wafer] = []

counter = 1
modules = []
for name in glob.glob(resultsDirectory + 'M*/*/commander*.root'):
    moduleName = name.split("/")[5].split("_")[0]
    if moduleName in modules:
        continue
    modules.append(moduleName)

    print "module #" + str(counter) + ": " +  moduleName
    counter += 1

    sensorCoordinates = getSensorCoordinates(partsDictionary, moduleName)
    wafer = sensorCoordinates[0]
    position = sensorCoordinates[1]
    if wafer == "?":
        continue

# choose histogram to use for summary plot
#    inputPath = 'Scurves/sig_scurveVcal_Vcal'
#    inputPath = 'BB3/rescaledThr'
    inputPath = 'PixelAlive/PixelAlive'
#    inputPath = 'Trim/sig_TrimThr0_vthrcomp'
#    inputPath = 'Trim/TrimMap'

    plots = produce2DPlotList(name, inputPath)
    if plots is None:
        continue

# convert input to binary plots if desired
#    makeBinaryPlots(plots,-0.1,9.9)
#    makeBinaryPlots(plots,5,-5)

    summaryPlot = makeMergedPlot(plots)
    summaryPlot.SetName(moduleName)
    info = {'position' : position, 'plot' : summaryPlot}
    plotDictionary[wafer].append(info)

for wafer in listOfWafers:
    if len(plotDictionary[wafer]):
        saveSensorWaferCanvas(wafer, inputPath, plotDictionary, 0, 1)
#        saveSensorWaferCanvas(wafer, inputPath, plotDictionary)
