#!/usr/bin/env python                                                                                                                                                                                                                                                                        
import os,sys#,string,urllib2

from testResultsTrackingTools import *
from componentTrackingTools import *

import datetime
import math

from optparse import OptionParser

import pandas as pd

parser = OptionParser()
parser.add_option("-i", "--file", dest="inputFileName",
                  help="path to input file containing a list of modules, one per line")
(arguments, args) = parser.parse_args()

from ROOT import TH1F, TCanvas, gStyle, TLegend

from ROOT import (kRed, kOrange, kYellow, kGreen,
                  kBlue, kViolet, kPink, kCyan, kBlack, kGray)

partsDictionary = producePartsDictionary()
if arguments.inputFileName:
    modules = [line.rstrip('\n') for line in open(arguments.inputFileName)]
else:
    modules = set(partsDictionary["module"].tolist())
    print len(modules)

if not os.path.exists('moduleGrades.json'):
    print "please run 'updateGradeDictionary.py' to produce module grade dictionary"
    sys.exit(0)

with open('moduleGrades.json', 'r') as fp:
    gradeDictionary = json.load(fp)


colors = ([kRed+1, kOrange+1, kYellow+1, kGreen+1,
          kBlue+1, kViolet+1, kPink+1, kCyan+1, kBlack, kGray])

failureModes = [
    "Dead DC w/ good Trim",
    "Dead DC w/ bad Trim",
    "Zombie",
    "Zero PH",
    "Partially Detached",
    "Dead Pixels",
    "Other",
]

start_date = datetime.datetime.strptime('2015-12-01 00:00:00', '%Y-%m-%d %H:%M:%S')

failureModePlot = TH1F("failureModePlot", ";;# ROCs", len(failureModes), 0, len(failureModes))
failureModePlot.SetStats(False)
for bin in range(len(failureModes)):
    failureModePlot.GetXaxis().SetBinLabel(bin+1,str(failureModes[bin]))

modePlots = []
counter = 0 
for mode in failureModes:
    plot = TH1F(mode, "ROC Failures by week;;# ROCs", 20, 0, 20)
    plot.SetStats(False)
    plot.SetLineColor(colors[counter])
    plot.SetLineWidth(3)
    counter += 1
    modePlots.append(plot)
modulesByWeekPlot = TH1F("modulesByWeek", "ROC Failures by week;;# ROCs", 20, 0, 20)
modulesByWeekPlot.SetStats(False)
modulesByWeekPlot.SetLineColor(1)
modulesByWeekPlot.SetLineWidth(3)

nModules = 0
nBadRocs = 0
for module in modules:
    if module not in gradeDictionary:
        print module, "missing from grade dictionary"
        continue
    if gradeDictionary[module]["Lessweb Grade"] == "I":
        print module, "not yet graded"
        continue

#    print nModules, "-", module, gradeDictionary[module]["Lessweb Grade"]
    nModules += 1
    data = gradeDictionary[module]
    date = partsDictionary[partsDictionary["module"] == module]["assembly date"].values[0]
    date_object = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    week = math.floor((date_object - start_date).days/7.)
    modulesByWeekPlot.Fill(week)

    for roc in range(15):
        if data["ROC"+str(roc)+" Failure"]:
            nBadRocs += 1
#            print module, roc, data["ROC"+str(roc)+" Failure"]
            failureModePlot.Fill(failureModes.index(data["ROC"+str(roc)+" Failure"]))
            modePlots[failureModes.index(data["ROC"+str(roc)+" Failure"])].Fill(week)

canvas = TCanvas("ROCFailures")

gStyle.SetTextFont(42)
failureModePlot.SetMarkerSize(3)
failureModePlot.Draw("bar")
failureModePlot.SetBarWidth(0.9)
failureModePlot.SetBarOffset(0.05)
canvas.SetBottomMargin(0.2)
#canvas.SetMargin(0.11,0.11,0.15,0.1)
failureModePlot.SetTitle("ROC Failure Mode Frequencies (" + str(nModules) + " modules)")
failureModePlot.SetFillColor(kRed+1)
failureModePlot.GetXaxis().SetLabelSize(0.07)
failureModePlot.GetXaxis().SetLabelOffset(0.011)


canvas.SaveAs("ROCFailures.pdf")




canvas2 = TCanvas("ROCFailures")
max = -999

for plot in modePlots:
    if plot.GetMaximum() > max:
        max = plot.GetMaximum()
if modulesByWeekPlot.GetMaximum() > max:
    max = modulesByWeekPlot.GetMaximum()

legend = TLegend(0.6, 0.6, 0.9, 0.9)
legend.SetBorderSize(0)
legend.SetFillStyle(0)


counter = 0
modulesByWeekPlot.Draw("c")
legend.AddEntry(modulesByWeekPlot, "# Modules", "L")
for plot in modePlots:
    plot.SetMaximum(1.1*max)
    legend.AddEntry(plot, failureModes[counter], "L")
    counter += 1
    plot.Draw("same c")
legend.Draw()
canvas2.SaveAs("ROCFailureByDate.pdf")
