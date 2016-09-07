#!/usr/bin/env python
import sys
import glob
from optparse import OptionParser
import pandas as pd
import json

from moduleSummaryPlottingTools import *
from ROOT import TFile, TCanvas, TLegend, THStack, TH1F, gDirectory
from ROOT import kBlack, kBlue, kRed, kGreen

gROOT.SetBatch()

inputDirName = '/Users/lantonel/PlotsAndTables/UniqueTestResults'

#######################################################

# script to make the following canvases

# where X = [dead pixels, bad bumps]


#  --- binary plots ---
# 1. number of X per ROC (1D)
#    stacked plot with
#    - installed modules
#    - all grade A
#    - all grade A+B
# 2. number of X per module (1D)
#    stacked plot with
#    - installed modules
#    - all grade A
#    - all grade A+B
# total X ROC map (2D):
#    3. installed modules
#    4. all grade A
#    5. all grade A+B
# total X module map (2D):
#    6. installed modules
#    7. all grade A
#    8. all grade A+B

#  --- raw value plots ---
# 9. post-trimming turn-on (1D)
#    stacked plot with
#    - installed modules
#    - all grade A
#    - all grade A+B
#10. post-trimming noise (1D)
#    stacked plot with
#    - installed modules
#    - all grade A
#    - all grade A+B

#######################################################

# outline:
#   load in module grades
#   for each 1D canvas in 1D configs
#     -get1DPlot for each series
#     -create1DCanvas with plots/config
#   for each 1D canvas in binary configs
#     -create1DPlot for each series
#     -create1DCanvas with plots/config
#   for each 2D canvas in 2D configs
#     -createROCPlot
#     -createModulePlot


# 1D binary canvas config:
#   title
#   path to 2D plot in root file
#   min, max for "true" entries
#   for each series:
#     -moduleList
#     -legendEntry
#     -fillColor

# 2D raw value canvas config:
#   title
#   path to 2D plot in root file

# 2D binary canvas config:
#   title
#   path to 2D plot in root file
#   min, max for "true" entries


# functions
#   create1DCanvas(plots)
#   create1DPlot(config)


#######################################################


#######################################################

def resetBadPlots(plots, module):

    with open('moduleInfo.json') as json_data:
        gradeDictionary = json.load(json_data)

        for roc in range(16):
            failure = gradeDictionary[module]["ROC"+str(roc)+" Failure"]
#            print module, str(roc), failure
#            if not pd.isnull(failure) and failure != "Partially Detached":
            if not pd.isnull(failure):
                print "skipping ROC " + str(roc) + ": " + str(failure)
                histo = plots[roc].Clone()
                histo.SetDirectory(0)
                histo.Reset()
                histo.SetTitle("bad")
                plots[roc] = histo

#######################################################

def create1DRawPlot(config, outputFile):

    canvas = TCanvas(config['title'].replace(" ","_"), "", 600, 600)
    stack = THStack("stack", config['title'])
    legend = TLegend(0.6, 0.6, 0.9, 0.9)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    th1s = []
    legendEntries = []
    for series in config['series']:
        counter = 0
        print "processing",str(len(series['modules'])),"modules for the",series['legendEntry'],"series"
        for module in series['modules']:
            inputFileList = glob.glob(inputDirName +'/' + module + '*/*/commander*.root')
            if not len(inputFileList):
                print "WARNING: No file found for module", module, " skipping..."
                continue
            inputFile = inputFileList[0]
            plots = produce1DPlotList(inputFile, config['path'])
            if not plots:
                continue
            sumPlot = makeSumPlot(plots)
            if not counter:
                th1 = sumPlot.Clone()
            else:
                th1.Add(sumPlot.Clone())
            counter += 1
        th1.SetFillColor(series['color'])
        th1.SetLineColor(kBlack)
        th1.SetStats(False)
        th1.GetXaxis().SetTitle(config['xunit'])
        th1.GetYaxis().SetTitle(config['yunit'])
        th1s.append(th1)
        legendEntries.append(series['legendEntry'])

    for th1 in th1s:
        stack.Add(th1)
    stack.Draw("HIST")
    stack.GetXaxis().SetTitle(config['xunit'])
    stack.GetYaxis().SetTitle(config['yunit'])
    for index in range(1,len(th1s)+1):
        legend.AddEntry(th1s[len(th1s)-index],legendEntries[len(th1s)-index],"F")
    legend.Draw()
    outputFile.cd()
    canvas.Write()

#######################################################

#######################################################

def create1DBinaryPlot(config, outputFile):

    canvas = TCanvas(config['title'].replace(" ","_"), "", 600, 600)
    stack = THStack("stack", config['title'])
    legend = TLegend(0.6, 0.6, 0.9, 0.9)
    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    th1s = []
    legendEntries = []

    for series in config['series']:
        th1 = TH1F(config['title'],config['title'], 100, 0, 300)
        print "processing",str(len(series['modules'])),"modules for the",series['legendEntry'],"series"
        counter = 0
        for module in series['modules']:
            inputFileList = glob.glob(inputDirName +'/' + module + '*/*/commander*.root')
            if not len(inputFileList):
                print "WARNING: No file found for module", module, " skipping..."
                continue
            inputFile = inputFileList[0]
            counter += 1
            print counter, inputFile
            plots = produce2DPlotList(inputFile, config['path'])
            if not plots:
                continue
            makeBinaryPlots(plots, config['min'], config['max'])
            sumPlot = makeSumPlot(plots)
            th1.Fill(sumPlot.Integral())
        th1.SetFillColor(series['color'])
        th1.SetLineColor(kBlack)
        th1.SetStats(False)
        th1.GetXaxis().SetTitle(config['xunit'])
        th1.GetYaxis().SetTitle(config['yunit'])
        th1s.append(th1)
        legendEntries.append(series['legendEntry'])

    for th1 in th1s:
        stack.Add(th1)
    stack.Draw("HIST")
    stack.GetXaxis().SetTitle(config['xunit'])
    stack.GetYaxis().SetTitle(config['yunit'])
    for index in range(1,len(th1s)+1):
        legend.AddEntry(th1s[len(th1s)-index],legendEntries[len(th1s)-index],"F")
    legend.Draw()
    outputFile.cd()
    canvas.Write()

#######################################################

def create2DBinaryPlots(config, outputFile):

    for series in config['series']:
        summary = None
        print "processing",str(len(series['modules'])),"modules for the",series['legendEntry'],"series"
        counter = 0
        for module in series['modules']:
            inputFileList = glob.glob(inputDirName +'/' + module + '*/*/commander*.root')
            if not len(inputFileList):
                print "WARNING: No file found for module", module, " skipping..."
                continue
            inputFile = inputFileList[0]
            counter += 1
            print counter, inputFile
            plots = produce2DPlotList(inputFile, config['path'])
            if not plots:
                continue
            makeBinaryPlots(plots, config['min'], config['max'])
            resetBadPlots(plots, module)
            if summary is None:
                summary = makeMergedPlot(plots)
            else:
                summary.Add(makeMergedPlot(plots))
        canvas = setupSummaryCanvas(summary, series['legendEntry'])
        canvas.SetName(config['title'].replace(" ", "_")+"_"+series['legendEntry'].replace(" ", "_"))
        canvas.SetTitle(config['title'])
        outputFile.cd()
        canvas.Write()



#######################################################
#######################################################
#######################################################


# load grades from the module DB file
with open('moduleInfo.json') as json_data:
    gradeDictionary = json.load(json_data)

# get lists of modules based on their grade and mounted status
installed = []
gradeANotInstalled = []
gradeBNotInstalled = []
gradeCNotInstalled = []
detachedROCs = []
for module in gradeDictionary:
    if not pd.isnull(gradeDictionary[module]["Position"]):
        installed.append(module)
    elif gradeDictionary[module]["Grade"] == "A":
        gradeANotInstalled.append(module)
    elif gradeDictionary[module]["Grade"] == "B":
        gradeBNotInstalled.append(module)
    elif gradeDictionary[module]["Grade"] == "C":
        gradeCNotInstalled.append(module)

    hasDetachedRoc = False
    for roc in range(16):
        if gradeDictionary[module]["ROC"+str(roc)+" Failure"] == "Partially Detached":
            hasDetachedRoc = True
            break
    if hasDetachedRoc:
        detachedROCs.append(module)

#installed = ['M-G-1-41','M-G-1-36','M-K-1-14']
#gradeANotInstalled = ['M-O-2-07','M-J-3-05','M-I-4-13']

allGradeA = installed + gradeANotInstalled
allModules = installed + gradeANotInstalled + gradeBNotInstalled + gradeCNotInstalled

installedConfig = {
    'modules' : installed,
    'legendEntry' : 'Installed',
    'color' : kGreen,
}

gradeANotInstalledConfig = {
    'modules' : gradeANotInstalled,
    'legendEntry' : 'Grade A',
    'color' : kBlack,
}

gradeBNotInstalledConfig = {
    'modules' : gradeBNotInstalled,
    'legendEntry' : 'Grade B',
    'color' : kBlue,
}

gradeCNotInstalledConfig = {
    'modules' : gradeCNotInstalled,
    'legendEntry' : 'Grade C',
    'color' : kRed,
}

gradeAConfig = {
    'modules' : allGradeA,
    'legendEntry' : 'Grade A',
    'color' : kBlack,
}

allModulesConfig = {
    'modules' : allModules,
    'legendEntry' : 'All Modules',
    'color' : kBlue,
}

detachedROCsConfig = {
    'modules' : detachedROCs,
    'legendEntry' : 'Partially Detached ROCs',
    'color' : kRed,
}



moduleListsToPlot = [installedConfig, gradeANotInstalledConfig, gradeBNotInstalledConfig, gradeCNotInstalledConfig]
#moduleListsToPlot = [installedConfig, gradeANotInstalledConfig, gradeBNotInstalledConfig]
#moduleListsToPlot = [installedConfig]



#######################################################
#######################################################
#######################################################

rawValue1DPlots = []

turnOn = {
    'title' : 'Pixel Turn-on Threshold',
    'path' : 'Scurves/dist_thr_scurveVcal_Vcal',
    'series' : moduleListsToPlot,
    'xunit' : 'VCal units',
    'yunit' : '# pixels',
}
#rawValue1DPlots.append(turnOn)

noise = {
    'title' : 'Pixel Noise',
    'path' : 'Scurves/dist_sig_scurveVcal_Vcal',
    'series' : moduleListsToPlot,
    'xunit' : 'VCal units',
    'yunit' : '# pixels',
}
#rawValue1DPlots.append(noise)

#######################################################

binary1DPlots = []

badBumps = {
    'title' : 'Bad Bumps per Module',
    'path' : 'BB3/rescaledThr',
    'series' : moduleListsToPlot,
    'min' : 5,
    'max' : 999,
    'xunit' : '# bad bumps',
    'yunit' : '# modules',
}
#binary1DPlots.append(badBumps)

#######################################################

binary2DPlots = []

badBumpMap = {
    'title' : 'Bad Bump Locations',
    'path' : 'BB3/rescaledThr',
#    'series' : [installedConfig, gradeAConfig],
    'series' : [allModulesConfig],
#    'series' : [detachedROCsConfig],
    'min' : 5,
    'max' : 999,
}
binary2DPlots.append(badBumpMap)

#######################################################
#######################################################
#######################################################

outputFile = TFile("Summaries.root", "RECREATE")

for config in rawValue1DPlots:
    create1DRawPlot(config, outputFile)

for config in binary1DPlots:
    create1DBinaryPlot(config, outputFile)

for config in binary2DPlots:
    create2DBinaryPlots(config, outputFile)


outputFile.Close()
