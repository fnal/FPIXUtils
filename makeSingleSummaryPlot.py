#!/usr/bin/env python
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--file", dest="inputFileName",
                  help="path to input file")
parser.add_option("-o", "--output", dest="outputFileName",
                  help="output file name (without extension)")
parser.add_option("-p", "--path", dest="pathToHistogram",
                  help="path to histogram, e.g. 'BB3/rescaledThr'")
parser.add_option("-t", "--type", dest="outputType",default="png",
                  help="output type (default = png)")
parser.add_option("-v", "--version", dest="version", default=0,
                  help="specify which version of plots to get (default = 0)")
parser.add_option("-z", "--logz", action="store_true", dest="logZ", default=False,
                  help="sets the z axis to a log scale")
(arguments, args) = parser.parse_args()

if not arguments.inputFileName:
    print "please specify input file";
    sys.exit(0)

if not arguments.pathToHistogram:
    print "please specify input histogram";
    sys.exit(0)

from moduleSummaryPlottingTools import *
from ROOT import TFile

gROOT.SetBatch()

if not os.path.exists(arguments.inputFileName):
    print "invalid input file, quitting"
    sys.exit(0)


canvas = produce2DSummaryPlot(arguments.inputFileName,
                              arguments.pathToHistogram,
                              arguments.version)

if canvas is None:
    sys.exit(0)

if arguments.outputFileName:
    name = arguments.outputFileName
else:
    name = arguments.pathToHistogram.replace("/","_") + "_V" + str(arguments.version)
if arguments.logZ:
    canvas.SetLogz()

if arguments.outputType is "root":
    outputFile = TFile(name+".root", "RECREATE")
    outputFile.cd()
    canvas.Write()
    outputFile.Close()
else:
    canvas.SaveAs(name+"."+arguments.outputType)
