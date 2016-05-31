#! /usr/bin/env python

"""
Author: John Stupak (jstupak@fnal.gov)
Date: 4-9-15
Usage: python xRayUpload.py <input root file>
"""

##############################################################
outputDir='.'
##############################################################

from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom
SE=SubElement

from glob import glob
import os
import subprocess
import sys
import zipfile
import re
import string
from datetime import datetime

DEBUG=False

modName = sys.argv[1]
moduleName = sys.argv[2]

topFile = "_XrayQualification-17C-KU-000000-0000_"
subFile000 = "000_HRData_40"
subFile001 = "001_HRData_120"
subFile002 = "002_HREfficiency_40"
subFile003 = "003_HREfficiency_80"
subFile004 = "004_HREfficiency_120"
subFile00c = "configfiles"
subFile00l = "logfiles"

f000File = "phrun02ma_*.*"
f001File = "phrun06ma_*.*"
f002File = "hr04ma_*.*"
f003File = "hr06ma_*.*"
f004File = "hr08ma_*.*"

new000 = "hrData_40.root"
new001 = "hrData_120.root"
new002 = "hrEff_40.root" 
new003 = "hrEff_80.root"
new004 = "hrEff_120.root"

f000lFile = "phrun02ma_*.log"
f001lFile = "phrun06ma_*.log"
f002lFile = "hr04ma_*.log"
f003lFile = "hr06ma_*.log"
f004lFile = "hr08ma_*.log"

newl000 = "hrData_40.log"
newl001 = "hrData_120.log"
newl002 = "hrEff_40.log" 
newl003 = "hrEff_80.log"
newl004 = "hrEff_120.log"

inifile = "elComandante.ini.tmp"
inidest = "elComandante.ini"
inipath = "~/Testing/FPIXUtils/MRWxRayConvert/"

testtime = "2016_00_00_00h00m_0000000000"

dirfile = moduleName + topFile + testtime

testFile = "testParameters.dat"
confFile = "configParameters.dat"
hotFile = "defaultMaskFile.dat"

tarend = ".tar.gz"

cdback = "../"
cd2back = "../../"
slash = "/"


##############################################################
################################################################
################################################################


os.system ("mkdir %s" % ( dirfile ))
os.chdir( dirfile )

os.system ( "mkdir %s" % ( subFile000 ))
os.system ( "mkdir %s" % ( subFile001 ))
os.system ( "mkdir %s" % ( subFile002 ))
os.system ( "mkdir %s" % ( subFile003 ))
os.system ( "mkdir %s" % ( subFile004 ))
os.system ( "mkdir %s" % ( subFile00c ))
os.system ( "mkdir %s" % ( subFile00l ))

os.system ("cp %s %s" % (cd2back+modName+slash+ testFile, subFile000 + slash + testFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ confFile, subFile000 + slash + confFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ hotFile, subFile000 + slash + hotFile))

os.system ("cp %s %s" % (cd2back+modName+slash+ testFile, subFile001 + slash + testFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ confFile, subFile001 + slash + confFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ hotFile, subFile001 + slash + hotFile))

os.system ("cp %s %s" % (cd2back+modName+slash+ testFile, subFile002 + slash + testFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ confFile, subFile002 + slash + confFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ hotFile, subFile002 + slash + hotFile))

os.system ("cp %s %s" % (cd2back+modName+slash+ testFile, subFile003 + slash + testFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ confFile, subFile003 + slash + confFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ hotFile, subFile003 + slash + hotFile))
    
os.system ("cp %s %s" % (cd2back+modName+slash+ testFile, subFile004 + slash + testFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ confFile, subFile004 + slash + confFile))
os.system ("cp %s %s" % (cd2back+modName+slash+ hotFile, subFile004 + slash + hotFile))
    
os.system ("cp %s %s" % (cdback+f000File, subFile000 ))
os.system ("cp %s %s" % (cdback+f001File, subFile001 ))
os.system ("cp %s %s" % (cdback+f002File, subFile002 ))
os.system ("cp %s %s" % (cdback+f003File, subFile003 ))    
os.system ("cp %s %s" % (cdback+f004File, subFile004 ))

os.chdir( subFile000 )
os.system ("rename %s %s %s" % ("*.root", new000, "*.root" ))
os.system ("rename %s %s %s" % ("*.log", newl000, "*.log" ))
os.chdir( cdback+ subFile001 )
os.system ("rename %s %s %s" % ("*.root", new001, "*.root" ))
os.system ("rename %s %s %s" % ("*.log", newl001, "*.log" ))
os.chdir( cdback+ subFile002 )
os.system ("rename %s %s %s" % ("*.root", new002, "*.root" ))
os.system ("rename %s %s %s" % ("*.log", newl002, "*.log" ))
os.chdir( cdback+ subFile003 )
os.system ("rename %s %s %s" % ("*.root", new003, "*.root" ))
os.system ("rename %s %s %s" % ("*.log", newl003, "*.log" ))
os.chdir( cdback+ subFile004 )
os.system ("rename %s %s %s" % ("*.root", new004, "*.root" ))
os.system ("rename %s %s %s" % ("*.log", newl004, "*.log" ))
os.chdir( cdback+ subFile00c )
os.system ("cp %s %s" % ( inipath + inifile, "./" ))
os.system ("rename %s %s %s" % (inifile, inidest, inifile ))


os.chdir( cd2back )
os.system( "tar -zcvf %s %s" % ( dirfile + tarend, dirfile ))

################################################################
