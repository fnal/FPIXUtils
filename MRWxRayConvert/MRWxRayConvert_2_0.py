#!/usr/local/bin/python
from ROOT import *
import subprocess
import os
import sys

XrayInDir = sys.argv[1]

hrFluxesUsed = [40,80,120]
dataFluxesUsed = [40,120]
dcNames = ['DCLowRate','DCHighRate']

def createRootFiles(hrFluxes, dataFluxes):
  for hrFlux in hrFluxes:
    outFile = TFile('hrEff_' + str(hrFlux) + '.root', "RECREATE")
    outFile.mkdir('HighRate')
    outFile.Close()
  for dataFlux in dataFluxes:
    outFile = TFile('hrData_' + str(dataFlux) + '.root', "RECREATE")
    outFile.mkdir('Xray')
    outFile.Close()

def splitRootFile(rootFile, hrFluxes, dataFluxes):
  inputFile = TFile(rootFile)
  inputFile.cd('Xray')
  for i in range(0,2):
    for plotKey in gDirectory.GetListOfKeys():
      if dcNames[i] in plotKey.GetName():
        outFile = TFile('hrData_' + str(dataFluxes[i]) + '.root', "UPDATE")
        inputHisto = inputFile.Get('Xray/' + plotKey.GetName())
        outFile.cd('Xray')
        inputHisto.Write(plotKey.GetName().split(dcNames[i])[0] + 'Ag' + plotKey.GetName().split(dcNames[i])[1])
        outFile.Close()
        inputFile.cd('Xray')
  inputFile.cd('HighRate')
  for j in range(0,3):
    for plotKey in gDirectory.GetListOfKeys():
      if 'V' + str(j) in plotKey.GetName():
        outFile = TFile('hrEff_' + str(hrFluxes[j]) + '.root', "UPDATE")
        inputHisto = inputFile.Get('HighRate/' + plotKey.GetName())
        histoTitle = plotKey.GetName()
        if 'V1' in histoTitle:
            histoTitle = histoTitle.replace("V1","V0")
        elif 'V2' in histoTitle:
            histoTitle = histoTitle.replace("V2","V0")
        outFile.cd('HighRate')
        inputHisto.Write(histoTitle)
        outFile.Close()
        inputFile.cd('HighRate')
  inputFile.Close()

def placeNewFiles(hrFluxes,dataFluxes):
  for i in range(0,2):
    for f in os.listdir('.'):
      if str(dataFluxes[i]) in f and 'hrData' in f:
        subprocess.call('mv ' + f + ' ' + str(topDir) + '/%03d'%i + '_HRData_' + str(dataFluxes[i]) + '/', shell = True)
  for j in range(0,3):
    for f in os.listdir('.'):
      if str(hrFluxes[j]) in f and 'hrEff' in f:
        subprocess.call('mv ' + f + ' ' + str(topDir) + '/%03d'%(j+2) + '_HREfficiency_' + str(hrFluxes[j]) + '/', shell = True)

def writeIniFile(hrFluxes, dataFluxes):
  inTmpFile = open('elComandante.ini.tmp')
  outTmpFile = open('elComandante.ini', 'w')
  for line in inTmpFile:
    if 'insertTestsHere' in line:
      line = 'Test = HRData@' + str(dataFluxes[0]) + 'MHz/cm2,HRData@' + str(dataFluxes[1]) + 'MHz/cm2>{HREfficiency@' + str(hrFluxes[0]) + 'MHz/cm2,HREfficiency@' + str(hrFluxes[1]) + 'MHz/cm2,HREfficiency@' + str(hrFluxes[2]) + 'MHz/cm2}' + '\n'
    outTmpFile.write(line)
  inTmpFile.close()
  outTmpFile.close()
  subprocess.call('mv elComandante.ini ' + topDir + '/configfiles', shell = True)

module = XrayInDir.split('_')[0]
date = XrayInDir.split('_')[2]
time = XrayInDir.split('_')[3]
number = XrayInDir.split('_')[4]

if '/' in number:
  number = int(number.replace("/", ""))
else:
  number = int(number)
number += 30

topDir = module + '_XrayQualification_' + date + '_' + time + '_' + str(number)
print 'Creating directory:' + topDir
mainDirList = ['HRData_' + str(dataFluxesUsed[0]),'HRData_' + str(dataFluxesUsed[1]),'HREfficiency_' + str(hrFluxesUsed[0]), 'HREfficiency_'  + str(hrFluxesUsed[1]), 'HREfficiency_' + str(hrFluxesUsed[2])]

configParamFilePath = XrayInDir + '/000_FPIXTest_p17/configParameters.dat'
testParamFilePath = XrayInDir + '/000_FPIXTest_p17/testParameters.dat'
defaultMaskFilePath = XrayInDir + '/000_FPIXTest_p17/defaultMaskFile.dat'

subprocess.call('mkdir ' + topDir, shell = True)
for i in range (0, len(mainDirList)):
  subprocess.call('mkdir ' + topDir + '/%03d'%i + '_' + mainDirList[i], shell = True)
  subprocess.call('cp ' + configParamFilePath + ' ' + topDir + '/%03d'%i + '_' + mainDirList[i], shell = True)
  subprocess.call('cp ' + testParamFilePath + ' ' + topDir + '/%03d'%i + '_' + mainDirList[i], shell = True)
  subprocess.call('cp ' + defaultMaskFilePath + ' ' + topDir + '/%03d'%i + '_' + mainDirList[i], shell = True)
subprocess.call('mkdir ' + topDir + '/configfiles', shell = True)
subprocess.call('mkdir ' + topDir + '/logfiles', shell = True)

createRootFiles(hrFluxesUsed,dataFluxesUsed)
splitRootFile(XrayInDir + '/000_FPIXTest_p17/highrate.root',hrFluxesUsed,dataFluxesUsed)
placeNewFiles(hrFluxesUsed,dataFluxesUsed)
writeIniFile(hrFluxesUsed,dataFluxesUsed)

subprocess.call('tar -zcvf ' + topDir + '.tar.gz ' + topDir, shell = True)
