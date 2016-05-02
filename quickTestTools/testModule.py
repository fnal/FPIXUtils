#!/usr/bin/env python

# script that runs a module through the Quicktest[1] procedure 
# used just before and after a module is mounted on a blade
# [1] Quicktest = pretest + pixelAlive (+ timing)
# N.B.: timing test is only run before mounting

# options:
# -m MODULE
# -s STAGE: "pre" or "post"
# -i HUBID

import datetime
import sys
from optparse import OptionParser



parser = OptionParser()
parser.add_option("-m", "--module", dest="module",
                  help="name of module being tested (REQUIRED)")
parser.add_option("-s", "--stage", dest="stage",
                  help="stage of testing - 'pre' or 'post' (REQUIRED)")
parser.add_option("-i", "--hubID", dest="hubID",
                  help="hubID value of module, 0-15 (REQUIRED)")
(arguments, args) = parser.parse_args()

if not arguments.module:
    print "please specify module name via '-m'";
    sys.exit(0)

if not arguments.stage:
    print "please specify testing stage via '-s'";
    sys.exit(0)

if not arguments.hubID:
    print "please specify hubID value via '-i'";
    sys.exit(0)


stamp = str(datetime.datetime.now())
dateStamp = stamp.split(' ')[0]
date = dateStamp
timeStamp = stamp.split(' ')[1]
dateStamp = dateStamp.split('-')[0][-2:] + dateStamp.split('-')[1] + dateStamp.split('-')[2]
time = timeStamp.split(':')[0] + 'h' + timeStamp.split(':')[1] + 'm'
timeStamp = timeStamp.split(':')[0] + timeStamp.split(':')[1]

print "stamp", stamp
print "dateStamp", dateStamp
print "date", date
print "timeStamp", timeStamp
print "time", time

###########################################
# create directory structure
###########################################


# MODULE_Quicktest-FNAL-DATETIME_DATETIMEV2_RANDOMSTRING
#   000_Quicktest_p17



###########################################
# create module configs
###########################################



###########################################
# run pXar command
###########################################


# -d MODULE_Quicktest-FNAL-DATETIME_DATETIMEV2_RANDOMSTRING
# e.g. "-d M-H-1-24_FPIXTest-17C-FNAL-160204-1503_2016-02-04_15h03m_1454619821"
# -r commander_Quicktest%s.root % STAGE

# -c testList%s.txt % STAGE

