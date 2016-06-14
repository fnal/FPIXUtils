#!/usr/bin/env python
import os,sys#,string,urllib2

from moduleTrackingTools import *
from componentTrackingTools import *

import datetime
import math

from optparse import OptionParser

import pandas as pd

parser = OptionParser()
parser.add_option("-i", "--file", dest="inputFileName",
                  help="path to input file containing a list of modules, one per line")
(arguments, args) = parser.parse_args()

from ROOT import gROOT, TH1F, TCanvas, gStyle, TLegend

from ROOT import (kRed, kOrange, kYellow, kGreen,
                  kBlue, kViolet, kPink, kCyan, kBlack, kGray)

gROOT.SetBatch()

if not os.path.exists('moduleInfo.json'):
    print "please run 'updateModuleDB.py' to produce database of module information"
    sys.exit(0)

with open('moduleInfo.json') as json_data:
    gradeDictionary = json.load(json_data)

if arguments.inputFileName:
    modules = [line.rstrip('\n') for line in open(arguments.inputFileName)]
else:
    modules = gradeDictionary.keys()


colors = (10 * [kRed+1, kOrange+1, kYellow+1, kGreen+1,
          kBlue+1, kViolet+1, kPink+1, kCyan+1, kBlack, kGray])

failureModes = [
    "Dead DC w/ bad Trim",
    "Dead DC w/ good Trim",
    "Bad Trim w/ no Bad DC",
    "Zombie",
    "Zero PH",
    "Low Iana / High Vana",
    "Iana Short",
    "Idig Short",
    "Partially Detached",
    "Dead Pixels",
    "Bad Bumps",
    "No Token Pass",
    "Unprogrammable",
    "Pulse Height Issue",
    "Other",
]

failureModeCategories = [
    "Debris",
    "Partially Detached",
    "Bad Bumps",
    "Dead Pixels",
    "Other"
]

# group together everything we think comes from debris
debrisFailureModes = [
    "Dead DC w/ bad Trim",
    "Dead DC w/ good Trim",
    "Bad Trim w/ no Bad DC",
    "Zombie",
    "Zero PH",
    "Low Iana / High Vana",
    "Iana Short",
    "Idig Short",
    "No Token Pass",
    "Unprogrammable",
    "Pulse Height Issue",
]


start_date = datetime.datetime.strptime('2015-12-02 00:00:00', '%Y-%m-%d %H:%M:%S')

failureModePlot = TH1F("failureModePlot", ";;# ROCs", len(failureModes), 0, len(failureModes))
failureModePlot.SetStats(False)
for bin in range(len(failureModes)):
    failureModePlot.GetXaxis().SetBinLabel(bin+1,str(failureModes[bin]))


modePlots = []
counter = 0
for mode in failureModes:
    plot = TH1F(mode, "ROC Failure Modes by batch;batch;ROC failure rate (%)", 30, 0, 30)
    plot.SetStats(False)
    plot.SetLineColor(colors[counter])
    plot.SetLineWidth(3)
    counter += 1
    modePlots.append(plot)

mechanismPlots = []
counter = 0
for mode in failureModeCategories:
    plot = TH1F(mode+" mechanism", "ROC Failure Mechanisms by batch;batch;ROC failure rate (%)", 30, 0, 30)
    plot.SetStats(False)
    plot.SetLineColor(colors[counter])
    plot.SetLineWidth(3)
    counter += 1
    mechanismPlots.append(plot)

modulesByBatchPlot = TH1F("modulesByBatch", "ROC Failure Modes by batch;batch;ROC failure rate (%)", 30, 0, 30)

nModules = 0
for module in modules:
    if module not in gradeDictionary:
        print module, "missing from grade dictionary"
        continue
    if gradeDictionary[module]["Grade"] == "I":
        print module, "not yet graded"
        continue
    if pd.isnull(gradeDictionary[module]["Received"]):
        print module, "not yet built"
        continue

    nModules += 1
    data = gradeDictionary[module]
    date = str(gradeDictionary[module]["Received"])
    date_object = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    week = math.floor((date_object - start_date).days/7.)
    # adjust for X-mas break
    if week >= 5:
        week -= 2
    modulesByBatchPlot.Fill(week)

    for roc in range(16):
        failureMode = data["ROC"+str(roc)+" Failure"]
        if pd.isnull(failureMode):
            continue
        if failureMode in failureModes:
            failureModePlot.Fill(failureModes.index(failureMode))
            modePlots[failureModes.index(failureMode)].Fill(week)
        if failureMode in failureModeCategories:
            mechanismPlots[failureModeCategories.index(failureMode)].Fill(week)
        elif failureMode in debrisFailureModes:
            mechanismPlots[failureModeCategories.index("Debris")].Fill(week)

canvas = TCanvas("ROCFailures","",800,400)
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

canvas2 = TCanvas("ROCFailuresByBatch")
max = -999
for plot in modePlots:
    plot.Divide(modulesByBatchPlot)
    plot.Scale(1./16*100)
    if plot.GetMaximum() > max:
        max = plot.GetMaximum()

legend = TLegend(0.6, 0.6, 0.9, 0.9)
legend.SetBorderSize(0)
legend.SetFillStyle(0)


counter = 0
for plot in modePlots:
    plot.SetMaximum(1.1*max)
    legend.AddEntry(plot, failureModes[counter], "L")
    counter += 1
#    plot.Draw("same c")
    plot.Draw("same")
legend.Draw()
canvas2.SaveAs("ROCFailureModesByBatch.pdf")

counter = 0
for plot in modePlots:
    canvas_ = TCanvas("ROCFailuresByBatch_"+failureModes[counter])
    legend_ = TLegend(0.6, 0.6, 0.9, 0.9)
    legend_.SetBorderSize(0)
    legend_.SetFillStyle(0)
    legend_.AddEntry(plot, failureModes[counter], "L")
    plot.Draw()
    legend_.Draw()
    canvas_.SaveAs("ROCFailureModesByBatch_"+failureModes[counter].replace("/","ith").replace(" ","_")+".pdf")
    counter += 1




canvas3 = TCanvas("ROCFailureMechanismsByBatch")
max = -999
for plot in mechanismPlots:
    plot.Divide(modulesByBatchPlot)
    plot.Scale(1./16*100)
    if plot.GetMaximum() > max:
        max = plot.GetMaximum()

legend = TLegend(0.6, 0.6, 0.9, 0.9)
legend.SetBorderSize(0)
legend.SetFillStyle(0)

counter = 0
for plot in mechanismPlots:
    plot.SetMaximum(1.1*max)
    legend.AddEntry(plot, failureModeCategories[counter], "L")
    counter += 1
#    plot.Draw("same c")
    plot.Draw("same")
legend.Draw()
canvas3.SaveAs("ROCFailureMechanismsByBatch.pdf")

counter = 0
for plot in mechanismPlots:
    canvas_ = TCanvas("ROCFailuresByBatch_"+failureModeCategories[counter])
    legend_ = TLegend(0.6, 0.6, 0.9, 0.9)
    legend_.SetBorderSize(0)
    legend_.SetFillStyle(0)
    legend_.AddEntry(plot, failureModeCategories[counter], "L")
    plot.Draw()
    legend_.Draw()
    canvas_.SaveAs("ROCFailureMechanismsByBatch_"+failureModeCategories[counter].replace("/","ith").replace(" ","_")+".pdf")
    counter += 1
