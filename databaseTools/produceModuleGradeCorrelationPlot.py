#!/usr/bin/env python                                                                                                                                                                                                                                                                        
import os,sys#,string,urllib2

from testResultsTrackingTools import *
from componentTrackingTools import *

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--file", dest="inputFileName",
                  help="path to input file containing a list of modules, one per line")
(arguments, args) = parser.parse_args()

from ROOT import TH2F, TCanvas, gStyle

if arguments.inputFileName:
    modules = [line.rstrip('\n') for line in open(arguments.inputFileName)]
else:
    partsDictionary = producePartsDictionary()
    modules = [module for module in partsDictionary]

if not os.path.exists('moduleGrades.json'):
    print "please run 'updateGradeDictionary.py' to produce module grade dictionary"
    sys.exit(0)

with open('moduleGrades.json', 'r') as fp:
    gradeDictionary = json.load(fp)


gradePlot = TH2F("Module Grade Comparison",";lessweb;MoReWeb",4,0,4,4,0,4)
gradePlot.SetStats(False)
xLabels = ["A", "B", "C", "I"]
yLabels = ["A", "B", "C", None]
for bin in range(len(xLabels)):
    gradePlot.GetXaxis().SetBinLabel(bin+1,str(xLabels[bin]))
for bin in range(len(yLabels)):
    gradePlot.GetYaxis().SetBinLabel(bin+1,str(yLabels[bin]))

nModules = 0
for module in modules:
    if module not in gradeDictionary:
        print module, "missing from grade dictionary"
        continue
    nModules += 1
    data = gradeDictionary[module]
    gradePlot.Fill(xLabels.index(data["lessweb grade"]), yLabels.index(data["moreweb grade"]))
    if data["lessweb grade"] != data["moreweb grade"]:
        if data["lessweb grade"] != "I" and data["moreweb grade"] != None:
            print module, "lessweb:", data["lessweb grade"], "moreweb:", data["moreweb grade"]


canvas = TCanvas()

gStyle.SetTextFont(42)
gradePlot.SetMarkerSize(3)
gradePlot.Draw("colz text")
canvas.SetMargin(0.11,0.11,0.15,0.1)
gradePlot.SetTitle("Module Grade Comparison (" + str(nModules) + " modules)")
gradePlot.GetXaxis().SetLabelSize(0.1)
gradePlot.GetXaxis().SetLabelSize(0.1)
gradePlot.GetYaxis().SetLabelSize(0.1)
gradePlot.GetXaxis().SetTitleSize(0.08)
gradePlot.GetYaxis().SetTitleSize(0.08)
gradePlot.GetXaxis().SetTitleOffset(0.8)
gradePlot.GetYaxis().SetTitleOffset(0.6)
gradePlot.GetXaxis().CenterTitle()
gradePlot.GetYaxis().CenterTitle()


canvas.SaveAs("ModuleGrades.pdf")
