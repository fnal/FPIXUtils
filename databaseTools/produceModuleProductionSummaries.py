#!/usr/bin/env python
import sys
import glob
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--directory", dest="inputDirName",
                  help="path to input dir")
(arguments, args) = parser.parse_args()

if not arguments.inputDirName:
    print "please specify input directory";
    sys.exit(0)

from moduleSummaryPlottingTools import *
from ROOT import TFile, TH1D
gROOT.SetBatch()

#######################################################

rocsToIgnoreBB3 = [
    { 'module' : 'M-G-1-17',
      'rocs'   : [-1]},
    { 'module' : 'M-G-1-39',
      'rocs'   : [-1]},
    { 'module' : 'M-G-1-43',
      'rocs'   : [-1]},
    { 'module' : 'M-G-2-10',
      'rocs'   : [-1]},
    { 'module' : 'M-H-1-15',
      'rocs'   : [-1]},
    { 'module' : 'M-H-1-23',
      'rocs'   : [14]},
    { 'module' : 'M-H-1-44',
      'rocs'   : [2]},
    { 'module' : 'M-H-2-14',
      'rocs'   : [8,15]},
    { 'module' : 'M-H-2-20',
      'rocs'   : [10]},
    { 'module' : 'M-H-2-37',
      'rocs'   : [-1]},
    { 'module' : 'M-J-1-14',
      'rocs'   : [15]},
    { 'module' : 'M-G-3-06',
      'rocs'   : [9]},
    { 'module' : 'M-H-1-02',
      'rocs'   : [14]},
    { 'module' : 'M-H-1-13',
      'rocs'   : [7]},
    { 'module' : 'M-B-4-48',
      'rocs'   : [4]},
    { 'module' : 'M-G-2-39',
      'rocs'   : [4,9,12]},
    { 'module' : 'M-G-3-50',
      'rocs'   : [10]},
    { 'module' : 'M-G-2-35',
      'rocs'   : [14]},
#    { 'module' : '',
#      'rocs'   : []},

]

rocsToIgnoreNew = [
    # almost dead ROC
    { 'module' : 'M-B-7-39',
      'rocs'   : [0]},
    # missing top rows
    { 'module' : 'M-G-1-08',
      'rocs'   : [5]},
    # bad bumps with dead pixel border
    { 'module' : 'M-G-2-28',
      'rocs'   : [7]},
    # bad bumps with dead pixel border
    { 'module' : 'M-G-2-35',
      'rocs'   : [14]},
    # dead DC in all 3
    { 'module' : 'M-G-2-39',
      'rocs'   : [4,9,12]},
    # dead DC
    { 'module' : 'M-H-1-23',
      'rocs'   : [14]},
    # bad bumps with dead pixel border
    { 'module' : 'M-G-1-37',
      'rocs'   : [14]},
    # almost dead ROC
    { 'module' : 'M-H-1-14',
      'rocs'   : [2]},
    # dead DC
    { 'module' : 'M-H-1-19',
      'rocs'   : [14]},
    # bad bumps with dead pixel border
    { 'module' : 'M-H-1-43',
      'rocs'   : [12]},
    # dead DC
    { 'module' : 'M-H-1-44',
      'rocs'   : [2]},
    # dead DC
    { 'module' : 'M-H-2-14',
      'rocs'   : [8]},
    # bad bumps with dead pixel border
    { 'module' : 'M-H-2-20',
      'rocs'   : [10]},
    # dead DC in 2, weird fit failure in 7...
    { 'module' : 'M-H-2-37',
      'rocs'   : [2,7]},
    # dead DC
    { 'module' : 'M-J-1-14',
      'rocs'   : [15]},
    # bad bumps with dead pixel border
    { 'module' : 'M-J-2-15',
      'rocs'   : [8]},
    # dead DC
    { 'module' : 'M-J-2-17',
      'rocs'   : [9]},
    # bad bumps with dead pixel border
    { 'module' : 'M-J-3-02',
      'rocs'   : [0]},
    # dead DCs
    { 'module' : 'M-J-3-14',
      'rocs'   : [6,9]},
    # bad bumps with dead pixel border
    { 'module' : 'M-J-3-16',
      'rocs'   : [0]},
    # dead DC
    { 'module' : 'M-J-3-22',
      'rocs'   : [5]},
    # dead DC
    { 'module' : 'M-J-3-26',
      'rocs'   : [14]},
    # several ROCs with possible BB3+PA border
    { 'module' : 'M-J-3-38',
      'rocs'   : [-1]},
    # dead DC
    { 'module' : 'M-G-3-06',
      'rocs'   : [9]},
    # dead DC
    { 'module' : 'M-H-1-13',
      'rocs'   : [7]},
    # dead DC
    { 'module' : 'M-H-1-06',
      'rocs'   : [7]},
    # dead DC
    { 'module' : 'M-H-2-21',
      'rocs'   : [14]},
    # dead DC in both
    { 'module' : 'M-J-3-03',
      'rocs'   : [3,10]},
    # dead DC
    { 'module' : 'M-G-3-50',
      'rocs'   : [10]},
    # dead DC
    { 'module' : 'M-I-2-24',
      'rocs'   : [15]},
    # dead row!
    { 'module' : 'M-J-2-29',
      'rocs'   : [15]},

]

#######################################################

inputs = []

pixelAliveConfig = {
    'path' : 'PixelAlive/PixelAlive',
    'min' : -0.1,
    'max' : 0.1,
}
#inputs.append(pixelAliveConfig)

bb3Config = {
    'path' : 'BB3/rescaledThr',
    'min' : 5,
    'max' : 999,
}
inputs.append(bb3Config)


rocsToIgnore = rocsToIgnoreBB3 + rocsToIgnoreNew
rocsToIgnore = rocsToIgnoreNew

nModulesAnalyzed = 0
nROCsAnalyzed = 0
nBadBumps = 0

#######################################################

def resetBadPlots(plots, name):

    global nROCsAnalyzed

    for rocToIgnore in rocsToIgnore:
        if rocToIgnore['module'] not in name:
            continue

        for roc in rocToIgnore['rocs']:
            print "skipping ROC " + str(roc)
            nROCsAnalyzed -= 1
            histo = plots[roc].Clone()
            histo.SetDirectory(0)
            histo.Reset()
            histo.SetTitle("bad")
            plots[roc] = histo

#######################################################

Summaries = []

for index in range(len(inputs)):
    Summaries.append(None)

RocPlots = []
for index in range(len(inputs)):
    RocPlots.append(None)

badBumpsPerROC = TH1D("dist_nBadBumps_ROC","# of bad bumps per ROC",100,0,200)
badBumpsPerModule = TH1D("dist_nBadBumps_Module","# of bad bumps per Module",100,0,500)

#for inputFile in glob.glob(arguments.inputDirName +'/M*_FPIXTest-m20C*/000_FPIXTest_m20/commander_FPIXTest.root'):
counter = 0
for inputFile in glob.glob(arguments.inputDirName +'/M*.root'):
    counter +=1

    module = inputFile.split("/")[-1].split("_")[0]
    print "processing module " + module


#    if counter < 10: continue



    badModule = False
    for rocToIgnore in rocsToIgnore:
        if rocToIgnore['module'] in inputFile:
            if rocToIgnore['rocs'][0] == -1:
                badModule = True
    if badModule:
        print "bad module, skipping..."
        continue



    nModulesAnalyzed = nModulesAnalyzed + 1
    print "adding module #" + str(nModulesAnalyzed)

    for index in range(len(inputs)):

        input = inputs[index]
        plots = produce2DPlotList(inputFile, input['path'])
        if plots is None:
            continue
        nROCsAnalyzed += 16
        makeBinaryPlots(plots, input['min'], input['max'])
        resetBadPlots(plots, inputFile)

        nBadInModule = 0
        for plot in plots:
            if plot.GetTitle() == "bad":
                continue
            nBadInModule += plot.Integral()
            badBumpsPerROC.Fill(plot.Integral())
        badBumpsPerModule.Fill(nBadInModule)
        nBadBumps += nBadInModule

        if Summaries[index] is None:
            Summaries[index] = makeMergedPlot(plots)
        else:
            Summaries[index].Add(makeMergedPlot(plots))

        if RocPlots[index] is None:
            RocPlots[index] = makeSumPlot(plots)
        else:
            RocPlots[index].Add(makeSumPlot(plots))

outputFile = TFile("Summaries.root", "RECREATE")
outputFile.cd()

badBumpsPerModule.Draw()
badBumpsPerModule.Write()
badBumpsPerROC.Draw()
badBumpsPerROC.Write()

for RocPlot in RocPlots:
    RocPlot.SetName("BB3")
    RocPlot.SetTitle("ROC Summary of Bad Bumps using " + str(nROCsAnalyzed) + " ROCs")
    RocPlot.Draw()
    RocPlot.Write()

for Summary in Summaries:
    name = Summary.GetName().replace("/","_")
#    Summary.SetName(name)
#    Summary.SetTitle("Summary of Bad Bumps using " + str(nModulesAnalyzed) + " modules")
    summaryCanvas = setupSummaryCanvas(Summary)
    summaryCanvas.SaveAs(name + ".png")
    summaryCanvas.Write()
outputFile.Close()


print nModulesAnalyzed, "modules analyzed"
print nROCsAnalyzed, "ROCs analyzed"
print nBadBumps, "bad bumps = ", str(100*nBadBumps/(4160*nROCsAnalyzed)), "%"
