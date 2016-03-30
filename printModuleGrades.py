#!/usr/bin/env python                                                                                                                                                                                                                                                                        
import os,sys,string,urllib2

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

nModules = 0
for module in modules:
    if module not in gradeDictionary:
        print module, "missing from grade dictionary"
        continue
    data = gradeDictionary[module]
    print module, "lessweb:", data["lessweb grade"], "moreweb:", data["moreweb grade"]
