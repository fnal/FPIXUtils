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

#################################################################

# function to decide whether the current input directory
# should be copied into the 'UniqueTestResults' directory
# and if so copy it and delete the previous one

def copyToUniqueTestResults(inputDir):

    module = inputDir.split('_')[0].split('/')[-1]
    
    outputDir = os.environ['HOME']+'/UniqueTestResults/'
    previous=glob(outputDir+module+'_*[0-9]')

    if len(previous)>1:
        print 'ERROR: directory already exists for module', module
        return
    # no pre-existing folder for this module, so we definitely want to copy ours
    # also there's nothing to delete
    if not previous:
        distutils.dir_util.copy_tree(inputDir,outputDir+inputDir.rstrip('/').split('/')[-1])
        return

    previousTemp = previous[0].split('/')[-1].split('_')[1].split('-')[1]
    currentTemp = inputDir.rstrip('/').split('/')[-1].split('_')[1].split('-')[1]

    previousDate = ''.join(previous[0].split('/')[-1].split('_')[1].split('-')[-2:])
    currentDate = ''.join(inputDir.rstrip('/').split('/')[-1].split('_')[1].split('-')[-2:])

    # if the current results are newer
    # we want to replace the previous with the current results folder,
    # unless the new results are at +17 and the old are at -20
    if currentDate > previousDate and not (previousTemp == "m20C" and currentTemp == "17C"):
        distutils.dir_util.copy_tree(inputDir,outputDir+inputDir.rstrip('/').split('/')[-1])
        distutils.dir_util.remove_tree(previous[0])
        return

#################################################################
#################################################################
#################################################################

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
        copyToUniqueTestResults(i)
        makeXML(i)
        distutils.dir_util.copy_tree(i,outputDir+'/'+os.path.basename(i))
else:
    for module in moduleNames:
        if module=='0': continue
        print module
        input=sorted(glob('/home/fnalpix?/allTestResults/'+module+'_*[0-9]'),key=lambda name: name.split('_')[-1])[-1]
        copyToUniqueTestResults(input)
        makeXML(input)
        distutils.dir_util.copy_tree(input,outputDir+'/'+os.path.basename(input))


