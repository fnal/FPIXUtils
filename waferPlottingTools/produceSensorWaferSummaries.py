#!/usr/bin/env python
from databaseTools.componentTrackingTools import *
from waferPlottingTools import *
import sys
import glob

gROOT.SetBatch()

resultsDirectory = '/Users/lantonel/PlotsAndTables/UniqueTestResults/'
secondaryResultsDirectory = ''

#resultsDirectory = '/Users/lantonel/PlotsAndTables/wafer_339_data/150V_m20C/'
#resultsDirectory = '/Users/lantonel/PlotsAndTables/wafer_339_data/330V/'
#resultsDirectory = '/Users/lantonel/PlotsAndTables/wafer_339_data/75V/'

#resultsDirectory = '/Users/lantonel/PlotsAndTables/wafer_339_data/Iana_30/'
#secondaryResultsDirectory = '/Users/lantonel/PlotsAndTables/wafer_339_data/150V_m20C/'

#resultsDirectory = '/Users/lantonel/PlotsAndTables/FNAL150VResults/'
#secondaryResultsDirectory = '/Users/lantonel/PlotsAndTables/UniqueTestResults/'

#secondaryResultsDirectory = '/Users/lantonel/PlotsAndTables/Purdue330VResults/'
#secondaryResultsDirectory = '/Users/lantonel/PlotsAndTables/Purdue150VResults/'




# parse list of module components
partsDictionary = producePartsDictionary()

if not os.path.exists('../databaseTools/moduleInfo.json'):
    print "please run 'updateModuleDB.py' to produce database of module information"
    sys.exit(0)

with open('../databaseTools/moduleInfo.json') as json_data:
    gradeDictionary = json.load(json_data)

# compile list of all Sensor wafers used
listOfWafers = getListOfSensorWafers(partsDictionary)

# use the Sensor wafer as the key
plotDictionary = {}
for wafer in listOfWafers:
    # each wafer contains a list of histograms and locations
    plotDictionary[wafer] = []

counter = 1
modules = []
listOfDirs = glob.glob(resultsDirectory + '/M*/*/commander*.root') + glob.glob(secondaryResultsDirectory + '/M*/*/commander*.root')
for name in listOfDirs:
    moduleName = name.split("/")[-3].split("_")[0]

    if moduleName in modules:
        continue
    modules.append(moduleName)

#for moduleName in modules:
#    if not len(glob.glob(resultsDirectory + '/'+moduleName+'*/*/commander*.root')):
#        continue
#    if not len(glob.glob(secondaryResultsDirectory + '/'+moduleName+'*/*/commander*.root')):
#        continue

#    primaryFile = glob.glob(resultsDirectory + '/'+moduleName+'*/*/commander*.root')[-1]
#    secondaryFile = glob.glob(secondaryResultsDirectory + '/'+moduleName+'*/*/commander*.root')[-1]


    sensorCoordinates = getSensorCoordinates(partsDictionary, moduleName)
    wafer = sensorCoordinates[0]
    position = sensorCoordinates[1]
    if wafer == "?":
        continue

#    if wafer != "333":
#        continue

#    if wafer[0] != "3":
#        continue

    moduleGrade = gradeDictionary[moduleName]['Grade']
    ivGrade = gradeDictionary[moduleName]['IV Grade']
    xrayGrade = gradeDictionary[moduleName]['X-Ray Grade']

    if "300V" in name:
        biasVoltage = "-300 V"
    else:
        biasVoltage = "-150 V"

    print "module #" + str(counter) + ": " +  moduleName
    print "   ", wafer, position
    counter += 1



##################################################
# choose histogram to use for summary plot
    inputPath = 'Scurves/sig_scurveVcal_Vcal'
#    inputPath = 'BB3/rescaledThr'
#    inputPath = 'PixelAlive/PixelAlive'
#    inputPath = 'Trim/sig_TrimThr0_vthrcomp'
#    inputPath = 'Trim/TrimMap'
##################################################


    plots = produce2DPlotList(name, inputPath)
    if plots is None:
        continue

#    plots = produce2DPlotList(primaryFile, inputPath)
#    secondaryPlots = produce2DPlotList(secondaryFile, inputPath)
#    for roc in range(16):
#        plots[roc].Add(secondaryPlots[roc], -1)

# convert input to binary plots if desired
#    makeBinaryPlots(plots,-0.1,9.9)
#    makeBinaryPlots(plots,5,-5)

    summaryPlot = makeMergedPlot(plots)
    summaryPlot.SetName(moduleName)
    info = {'position' : position,
            'plot' : summaryPlot,
            'module' : moduleName,
            'grade' : moduleGrade,
            'ivgrade' : ivGrade,
            'xraygrade' : xrayGrade,
            'bias' : biasVoltage
            }
    plotDictionary[wafer].append(info)



for wafer in listOfWafers:
    if len(plotDictionary[wafer]):
        saveSensorWaferCanvas(wafer, inputPath, plotDictionary, 1,10)
#        saveSensorWaferCanvas(wafer, inputPath, plotDictionary)
