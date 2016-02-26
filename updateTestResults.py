#!/usr/bin/env python                                                                                                                                                                                     
# This script copies just one root file per module from the test results directory
# It takes the most recent -20 result (if one exists), 
# if not it takes the most recent +17 result
# ignores files smaller than 1MB

#import sys
from os import path
from glob import glob
from shutil import copy
from sys import exit


inputDir = '/Users/lantonel/PlotsAndTables/ProductionResults/'
outputDir = '/Users/lantonel/PlotsAndTables/ModuleTestResults/'


badResultsList = [

    'M-H-1-14_ElComandanteTest_2015-12-28_12h25m_1451327122',
    'M-J-1-37_FPIXTest-m20C-FNAL-160217-1140_2016-02-17_11h40m_1455730843',
    'M-H-2-02_FPIXTest-m20C-FNAL-151215-1445_2015-12-15_14h45m_1450212335',
    'M-G-1-43_FPIXTest-m20C-FNAL-160212-1203_2016-02-12_12h04m_1455300281',
    'M-G-2-10_FPIXTest-m20C-FNAL-160202-1433_2016-02-02_14h33m_1454445219',
    'M-G-1-39_FPIXTest-m20C-FNAL-160126-1147_2016-01-26_11h47m_1453830436',
    'M-G-1-17_FPIXTest-m20C-FNAL-160126-1147_2016-01-26_11h47m_1453830436',

]

fileList = glob(inputDir+'/M*/*/commander_*.root')
fileList.sort(key=path.getmtime)

moduleList = []
p17Dir = {}
m20Dir = {}
for name in fileList:

    isBad = False
    for result in badResultsList:
        if result in name:
            isBad = True
            break
    if isBad:
        continue

    if path.getsize(name) < 1000000:
        continue
    moduleName = name.split("/")[5].split("_")[0]
    moduleList.append(moduleName)
    if 'p17' in name and name not in p17Dir:
        p17Dir[moduleName] = name
    elif 'm20' in name and name not in m20Dir:
        m20Dir[moduleName] = name

uniqueModuleList = sorted(list(set(moduleList)))

uniqueFileList = []

for moduleName in uniqueModuleList:
    if moduleName in m20Dir:
        uniqueFileList.append(m20Dir[moduleName])
    elif moduleName in p17Dir:
        uniqueFileList.append(p17Dir[moduleName])

print "processed",len(uniqueModuleList),"modules"

for inputFile in uniqueFileList:
    moduleName = inputFile.split("/")[5].split("_")[0]
    temp = 'XXX'
    if 'm20' in inputFile:
        temp = 'm20'
    elif 'p17' in inputFile:
        temp = 'p17'
    outputFileName = moduleName+'_'+temp+'.root'
    
    print "copying", temp, "result for module", moduleName
    copy(inputFile, outputDir + "/" + outputFileName)

