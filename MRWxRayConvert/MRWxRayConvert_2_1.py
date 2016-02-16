#!/usr/local/bin/python
from ROOT import *
import subprocess
import os
import sys

XrayInDir = sys.argv[1]

inDate = int(raw_input('Enter date of X-ray results (MMDD):'))
inDateStr = str('%04d'%inDate)
print inDateStr

hrFluxesUsed = [40,80,120]
dataFluxesUsed = [40,120]

def placeNewFiles(hrFluxes,dataFluxes):
  fileCounter = 0
  for f in os.listdir(XrayInDir + '/000_FPIXTest_p17/'):
    for i in range(0,2):
      if 'dc' + '%02d'%((i-1)*10 + 15) + '_' + lowerModule + '_' + str(inDateStr) in f:
        subprocess.call('cp ' + XrayInDir + '/000_FPIXTest_p17/' + f + ' ' + str(topDir) + '/%03d'%i + '_HRData_' + str(dataFluxes[i]) + '/', shell = True)
        fileCounter += 1
        changeFile = TFile(str(topDir) + '/%03d'%i + '_HRData_' + str(dataFluxes[i]) + '/dc' + '%02d'%((i-1)*10 + 15) + '_' + lowerModule + '_' + str(inDateStr) + '.root', "UPDATE")
        changeFile.cd('Xray')
        for plotKey in gDirectory.GetListOfKeys():
            histoTitle = plotKey.GetName()
            if 'DCLowRate' in histoTitle:
                histoTitle = histoTitle.replace("DCLowRate","Ag")
                plotKey.SetName(histoTitle)
            elif 'DCHighRate' in histoTitle:
                histoTitle = histoTitle.replace("DCHighRate","Ag")
                plotKey.SetName(histoTitle)
        changeFile.Close()
    for j in range(0,3):
      if 'hr' + '%02d'%((j+1)*5) + 'ma_' + lowerModule +'_' + str(inDateStr) in f:
        subprocess.call('cp ' + XrayInDir + '/000_FPIXTest_p17/' + f + ' ' + str(topDir) + '/%03d'%(j+2) + '_HREfficiency_' + str(hrFluxes[j]) + '/', shell = True)
        fileCounter += 1
        changeFile = TFile(str(topDir) + '/%03d'%(j+2) + '_HREfficiency_' + str(hrFluxes[j]) + '/hr' + '%02d'%((j+1)*5) + 'ma_' + lowerModule + '_' + str(inDateStr) + '.root', "UPDATE")
        changeFile.cd('HighRate')
        for plotKey in gDirectory.GetListOfKeys():
            histoTitle = plotKey.GetName()
            if 'V1' in histoTitle:
                histoTitle = histoTitle.replace("V1","V0")
                plotKey.SetName(histoTitle)
            elif 'V2' in histoTitle:
                histoTitle = histoTitle.replace("V2","V0")
                plotKey.SetName(histoTitle)
        changeFile.Close()
  if fileCounter != 5:
    sys.exit('Abort: Desired root files not found')
    subprocess.call('rm -r ' + topDir, shell = True)


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

lowerModule = module.replace("-","").lower()
print lowerModule

if '/' in number:
  number = int(number.replace("/", ""))
else:
  number = int(number)
number += 30 + inDate  #gives new id number if new results for same module

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

placeNewFiles(hrFluxesUsed,dataFluxesUsed)
writeIniFile(hrFluxesUsed,dataFluxesUsed)
subprocess.call('tar -zcvf ' + topDir + '.tar.gz ' + topDir, shell = True)
