#!/usr/bin/env python

# script that runs a module through the Quicktest[1] procedure 
# used just before and after a module is mounted on a blade
# [1] Quicktest = (timing+)pixelAlive+BB3
# N.B.: timing test is only run before mounting

# options:
# -m MODULE
# -s STAGE: "pre" or "post" (case-insensitive)
# -i HUBID

import datetime
import sys
import random
import os
import subprocess
import glob
from optparse import OptionParser



# site-specific directory names

outputDir_ = "/home/fnalpxar/quicktestResults/"
#pxarDir_ = "/home/fnalpxar/pxar/"
pxarDir_ = "/home/fnalpxar/pxar/"
fpixutilsDir_ = "/home/fnalpxar/FPIXUtils/quickTestTools/"

parser = OptionParser()
parser.add_option("-m", "--module", dest="module",
                  help="name of module being tested (REQUIRED)")
parser.add_option("-s", "--stage", dest="stage",
                  help="stage of testing - 'pre' or 'post' (REQUIRED)")
parser.add_option("-i", "--hubID", dest="hubID",
                  help="hubID value of module, 0-15 (REQUIRED for 'pre' test)")
parser.add_option("-d", "--vdig", dest="vdig", default='8', help="vdig to run module at (Only works with 'pre' test)")
parser.add_option("-l", "--level", dest="level", default='12', help="level to run DTB at (Only works with 'pre' test)")
parser.add_option("-t", "--timing", action="store_true", dest="timing", default=False, help="Adjust Timings (Should only use with 'pre' test)")
parser.add_option("-v", "--version", dest="version", default="4.6", help="Which version of pXar to use. Options are 4.5 or 4.6")
(arguments, args) = parser.parse_args()

if not arguments.module:
    print "please specify module name via '-m'";
    sys.exit(0)

if not arguments.stage:
    print "please specify testing stage via '-s'";
    sys.exit(0)
elif arguments.stage.lower() not in ["pre","post"]:
    print "invalid stage"
    sys.exit(0)
if not arguments.hubID and arguments.stage.lower() == 'pre':
    print "please specify hubID value via '-i'";
    sys.exit(0)

if arguments.version == "4.5":
    pxarDir_ = "/home/fnalpxar/pxar/"
elif arguments.version == "4.6":
    pxarDir_ = "/home/fnalpxar/pxar_4.6/"

stage = arguments.stage.lower().capitalize()

###########################################
###########################################
###########################################

if stage == "Pre":

    ###########################################
    # parse date and time
    ###########################################

    stamp = str(datetime.datetime.now())
    dateStamp = stamp.split(' ')[0]
    date = dateStamp
    timeStamp = stamp.split(' ')[1]
    dateStamp = dateStamp.split('-')[0][-2:] + dateStamp.split('-')[1] + dateStamp.split('-')[2]
    time = timeStamp.split(':')[0] + 'h' + timeStamp.split(':')[1] + 'm'
    timeStamp = timeStamp.split(':')[0] + timeStamp.split(':')[1]
    directoryName = arguments.module + '_Quicktest-p17-FNAL-' + dateStamp + '-' + timeStamp + '_' + date + '_' + time + '_' + str(random.randint(1000000000,9999999999))

    ###########################################
    # create output directory
    ###########################################

    testDir = outputDir_ + "/" + directoryName
    os.makedirs(testDir)

    ###########################################
    # get module configs
    ###########################################
    print "You are too stupid to before"
    os.system("scp 'uicpirepix2@bender.phy.uic.edu:/home/uicpirepix2/ProductionTestResults/"+arguments.module+"_FPIXTest-m20C*/000_FPIXTest_m20/*.dat' "+testDir)
    os.system("sed -i 's|testboardName [A-Z0-9_][A-Z0-9_]*|testboardName *|' "+testDir+"/configParameters.dat")
    os.system("sed -i 's|hubId [0-9][0-9]*|hubId "+arguments.hubID+"|' "+testDir+"/configParameters.dat")
    os.system("sed -i 's|level   [0-9][0-9]*|level   "+arguments.level+"|' "+testDir+"/tbParameters.dat")
    os.system("sed -i 's|vdig       [0-9][0-9]*|vdig       "+arguments.vdig+"|' "+testDir+"/dacParameters35_C*.dat")
    if arguments.timing and arguments.version=="4.6":
        os.system("sed -i 's|basea   0x.*|basea   0xdb|' "+testDir+"/tbmParameters_C0*.dat")
        os.system("sed -i 's|basee   0x.*|basee   0xc8|' "+testDir+"/tbmParameters_C0a.dat")

###########################################
###########################################
###########################################

elif stage == "Post":

    testDir = sorted(glob.glob(outputDir_ + "/" + arguments.module + "*"))[-1]

    if os.path.isdir(testDir + "/000_Quicktest_p17"):
        testDir += "/000_Quicktest_p17/"

###########################################
###########################################
###########################################

# run pXar command
###########################################
if arguments.timing and arguments.version=="4.5":
    os.system("cat " + fpixutilsDir_ + "/testList" + stage + ".txt" + \
          " | sed '1 i\\timing' |" + \
          pxarDir_ + "/bin/pXar -d " + testDir + " -T 35 -v DEBUG -r commander_Quicktest" + stage + ".root")
else:
    os.system("cat " + fpixutilsDir_ + "/testList" + stage + ".txt" + \
          " | " + \
          pxarDir_ + "/bin/pXar -d " + testDir + " -T 35 -v DEBUG -r commander_Quicktest" + stage + ".root")

###########################################
# print relevant lines from log file
###########################################

linesToPrint = [
    "number of dead pixels",
    "number of dead bumps",
    "Functional",
#    "The fraction of properly decoded events is",
#    "Timings are"
    ]

print
print "TEST RESULT SUMMARY:"
print "--------------------"
log = open(testDir + "/commander_Quicktest" + stage + ".log")
for line in log.readlines():
    if any(hook in line for hook in linesToPrint):
        print line.rstrip()
