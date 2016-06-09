#! /usr/bin/env python

"""
Author: John Stupak (jstupak@fnal.gov)
Date: 4-9-15
Usage: python uploadTest.py <testName> <isCold> [input dir]
"""

from config import *
from lessWeb import *
from sys import argv
#from shutil import copytree
import distutils.dir_util
import os

outputDir=os.environ['HOME']+'/ProductionTestResults'
#outputDir=os.environ['HOME']+'/john'

"""
if len(argv)>2:
    testName=argv[1]
    doCold=argv[2]
    inputDirs=None
    if len(argv)>3:
        inputDirs=argv[3:]
else:
    raise Exception("You must specify if test was performed cold")
"""

# function to decide whether the current input directory 
# should be copied into the 'UniqueTestResults' directory
# and if so copy it and delete the previous one
#
# cases:
# isP17, isM20
# previousExisting or not
# if previous exists, is it m20 or not

def copyToUniqueTestResults(inputDir):
    module = inputDir.split('/')[4].split('_')[0]
    print module
    previous=sorted(glob('/home/fnalpix?/UniqueTestResults/'+module+'_*[0-9]'),key=lambda name: name.split('_')[-1])
    



if len(argv)>1: inputDirs=argv[1:]
else: inputDirs=None

if inputDirs:
    for inputDir in inputDirs:
        inputs=glob(inputDir)
        if not inputs:
            print 'ERROR: input directory',inputDir,'not found'
            exit()
        if len(inputs)>1:
            print 'ERROR: multiple input directories match string',inputDir
            exit()
        i=inputs[0]
        makeXML(i)
        distutils.dir_util.copy_tree(i,outputDir+'/'+os.path.basename(i))
else:
    for module in moduleNames:
        if module=='0': continue
        print module
        input=sorted(glob('/home/fnalpix?/allTestResults/'+module+'_*[0-9]'),key=lambda name: name.split('_')[-1])[-1]
        makeXML(input)
        distutils.dir_util.copy_tree(input,outputDir+'/'+os.path.basename(input))

    
