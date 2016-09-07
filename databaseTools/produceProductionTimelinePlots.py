#!/usr/bin/env python
import os,sys#,string,urllib2
import json

from moduleTrackingTools import *
from componentTrackingTools import *

import datetime
import math

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--file", dest="inputFileName",
                  help="path to input file containing a list of modules, one per line")
(arguments, args) = parser.parse_args()

from ROOT import gROOT, TH1F, TCanvas, gStyle, TLegend, TFile

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


start_date = datetime.datetime.strptime('2015-12-02 00:00', '%Y-%m-%d %H:%M')

modulesByWeekPlot = TH1F("modulesByWeek", "Number of modules by batch; batch; # modules", 30, 0, 30)
modulesByWeekPlot.SetStats(False)
modulesByWeekPlot.SetLineColor(1)
modulesByWeekPlot.SetLineWidth(3)


nBins = 12
maxDays = 60
assemblyTimePlot = TH1F("assemblyTime", "Module assembly & testing times; time [days]; # modules", nBins, 0, maxDays)
assemblyTimePlot.SetStats(False)
assemblyTimePlot.SetLineColor(kRed+1)
assemblyTimePlot.SetLineWidth(3)
assemblyTimePlotPurdue = TH1F("assemblyTimePurdue", "Module assembly & testing times; time [days]; # modules", nBins, 0, maxDays)
assemblyTimePlotPurdue.SetStats(False)
assemblyTimePlotPurdue.SetLineColor(kOrange+1)
assemblyTimePlotPurdue.SetLineWidth(3)
assemblyTimePlotUNL = TH1F("assemblyTimeUNL", "Module assembly & testing times; time [days]; # modules", nBins, 0, maxDays)
assemblyTimePlotUNL.SetStats(False)
assemblyTimePlotUNL.SetLineColor(kYellow+1)
assemblyTimePlotUNL.SetLineWidth(3)

testingTimePlot = TH1F("testingTime", "Module assembly & testing times; time [days]; # modules", nBins, 0, maxDays)
testingTimePlot.SetStats(False)
testingTimePlot.SetLineColor(kBlue+1)
testingTimePlot.SetLineWidth(3)
totalTimePlot = TH1F("totalTime", "Module assembly & testing times; time [days]; # modules", nBins, 0, maxDays)
totalTimePlot.SetStats(False)
totalTimePlot.SetLineColor(kBlack)
totalTimePlot.SetLineWidth(3)

nModules = 0
for module in modules:
    if module not in gradeDictionary:
        print module, "missing from grade dictionary"
        continue
    if pd.isnull(gradeDictionary[module]["Judged"]):
        print module, "not yet judged"
        continue

    data = gradeDictionary[module]

    nModules += 1

    date = str(data["Received"])
    if not pd.isnull(data["Shipped"]):
        ship = str(data["Shipped"])
    else:
        ship = '2015-11-02 00:00:00'
    if not pd.isnull(data["Judged"]):
        judge = str(data["Judged"])
    else:
        judge = '2015-11-02 00:00:00'

    date_object = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    ship_object = datetime.datetime.strptime(ship, '%Y-%m-%d %H:%M:%S')
    judge_object = datetime.datetime.strptime(judge, '%Y-%m-%d %H:%M:%S')

    week = math.floor((date_object - start_date).days/7.)
    # adjust for X-mas break
    if week >= 5:
        week -=2
    
    modulesByWeekPlot.Fill(week)
    assemblyTime = math.floor((ship_object - date_object).days)
    if assemblyTime:
        if assemblyTime > maxDays:
            assemblyTime = maxDays - 0.1
        assemblyTimePlot.Fill(assemblyTime)
        if data['assembly site'] == 'Purdue':
            assemblyTimePlotPurdue.Fill(assemblyTime)
        elif data['assembly site'] == 'Nebraska':
            assemblyTimePlotUNL.Fill(assemblyTime)
    testingTime = math.floor((judge_object - ship_object).days)
    if testingTime:
        if testingTime > maxDays:
            testingTimePlot.Fill(maxDays - 0.1)
        else:
            testingTimePlot.Fill(testingTime)
    totalTime = math.floor((judge_object - date_object).days)
    if totalTime:
        if totalTime > maxDays:
            totalTimePlot.Fill(maxDays - 0.1)
        else:
            totalTimePlot.Fill(totalTime)




outputFile = TFile("Times.root", "RECREATE")
outputFile.cd()

timeCanvas = TCanvas("timePlot")
globalMax = -999
if assemblyTimePlot.GetMaximum() > globalMax:
    globalMax = assemblyTimePlot.GetMaximum()
if testingTimePlot.GetMaximum() > globalMax:
    globalMax = testingTimePlot.GetMaximum()
if totalTimePlot.GetMaximum() > globalMax:
    globalMax = totalTimePlot.GetMaximum()

globalMax *= 1.1
assemblyTimePlot.SetMaximum(globalMax)
testingTimePlot.SetMaximum(globalMax)
totalTimePlot.SetMaximum(globalMax)


assemblyTimePlot.Draw()
testingTimePlot.Draw("same")
totalTimePlot.Draw("same")


timeLegend = TLegend(0.5, 0.6, 0.9, 0.9)
timeLegend.SetBorderSize(0)
timeLegend.SetFillStyle(0)
timeLegend.AddEntry(0, str(nModules) + " modules processed", "H")
timeLegend.AddEntry(assemblyTimePlot, "Assembly Time", "L")
timeLegend.AddEntry(testingTimePlot, "Testing Time", "L")
timeLegend.AddEntry(totalTimePlot, "Total Processing Time", "L")
timeLegend.Draw()

timeCanvas.Write()
timeCanvas.SaveAs("Times.pdf")

##########

assemblyCanvas = TCanvas("assemblyPlot")
globalMax = -999
if assemblyTimePlot.GetMaximum() > globalMax:
    globalMax = assemblyTimePlot.GetMaximum()
if assemblyTimePlotPurdue.GetMaximum() > globalMax:
    globalMax = testingTimePlotPurdue.GetMaximum()
if assemblyTimePlotUNL.GetMaximum() > globalMax:
    globalMax = totalTimePlotUNL.GetMaximum()

globalMax *= 1.1
assemblyTimePlot.SetMaximum(globalMax)
assemblyTimePlotPurdue.SetMaximum(globalMax)
assemblyTimePlotUNL.SetMaximum(globalMax)


assemblyTimePlot.Draw()
assemblyTimePlotPurdue.Draw("same")
assemblyTimePlotUNL.Draw("same")


assemblyLegend = TLegend(0.5, 0.6, 0.9, 0.9)
assemblyLegend.SetBorderSize(0)
assemblyLegend.SetFillStyle(0)
assemblyLegend.AddEntry(0, str(nModules) + " modules processed", "H")
assemblyLegend.AddEntry(assemblyTimePlot, "Assembly time (Total)", "L")
assemblyLegend.AddEntry(assemblyTimePlotPurdue, "Assembly time (Purdue)", "L")
assemblyLegend.AddEntry(assemblyTimePlotUNL, "Assembly time (UNL)", "L")
assemblyLegend.Draw()

assemblyCanvas.Write()
assemblyCanvas.SaveAs("AssemblyBySite.pdf")

######

canvas2 = TCanvas("ModulesPerBatch")
#legend = TLegend(0.6, 0.6, 0.9, 0.9)
#legend.SetBorderSize(0)
#legend.SetFillStyle(0)

modulesByWeekPlot.Draw("bar")
modulesByWeekPlot.SetBarWidth(0.9)
modulesByWeekPlot.SetBarOffset(0.05)
#modulesByWeekPlot.SetMaximum(1.5*modulesByWeekPlot.GetMaximum())
#legend.AddEntry(modulesByWeekPlot, "# Modules", "L")
#legend.Draw()
canvas2.SaveAs("NModulesPerBatch.pdf")
outputFile.Close()
