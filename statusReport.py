#!/usr/bin/env python
import sys
import os
import time
from config import moduleNames, goodModuleNames
import glob
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-m", "--mode", dest="mode",
                  help="either 'test' or 'errors'")
(arguments, args) = parser.parse_args()

if not arguments.mode:
    print "please specify mode";
    sys.exit(0)
if arguments.mode.lower() not in ['test','errors']:
    print "invalid mode"
    sys.exit(0)

mode = arguments.mode.lower()

columnWidth = 15
tbLine = ["TB:"]
idLine = ["module ID:"]

inputDir = os.path.expanduser('~') + "/allTestResults/"

tbs = []
inputFiles = []
for index, module in enumerate(moduleNames):

    if module == "0":
        continue

    tbs.append(index)
    testDirs = glob.glob(inputDir + "/" + module + "_*")
    testDirs.sort(key=lambda x: os.path.getmtime(x))
    testDir = testDirs[-1]
    inputFileList = []
    while len(inputFileList) == 0:
       inputFileList = glob.glob(testDir + "/" + "000*/commander_*.log")
    inputFile = inputFileList[0]
    inputFiles.append(inputFile)

for index, module in enumerate(goodModuleNames):
    tbLine.append(str(tbs[index]))
    idLine.append(module)



os.system('clear')
for entry in tbLine:
    print " "*(columnWidth-len(entry)) + entry,
print
for entry in idLine:
    print " "*(columnWidth-len(entry)) + entry,
print

if mode == 'errors':
    while 1:
        time.sleep(1)
        output = ["# pXar errors:"]
        for inputFile in inputFiles:
            nErrors = 0
            with open(inputFile) as data_file:
                for line in data_file:
                    if "ERROR:" in line:
                        nErrors +=1
            output.append(str(nErrors))
            sys.stdout.write("\r")
            for entry in output:
                sys.stdout.write(" "*(columnWidth-len(entry)) + entry + " ")
            sys.stdout.flush()

if mode == 'test':
    while 1:
        time.sleep(1)
        output =  ["current test:"]
        for inputFile in inputFiles:
            test = ""
            with open(inputFile) as data_file:
                for line in data_file:
                    if "doTest()" in line and "done" not in line:
                        test = line.split(" ")[7].split("::")[0].replace("PixTest","")
            output.append(test)
            sys.stdout.write("\r")
            for entry in output:
                sys.stdout.write(" "*(columnWidth-len(entry)) + entry + " ")
            sys.stdout.flush()
