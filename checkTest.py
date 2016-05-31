#! /usr/bin/env python

"""
Author: John Stupak (jstupak@fnal.gov)
Date: 5-2-15
Usage: ./checkTest.py <test>
"""

from Comparison import *
from sys import argv
from config import *
from glob import glob
import os

testResultDir=os.environ['HOME']+'/allTestResults'
#testResultDir='/Users/jstupak/CMS/pixel/ShareTestResults/elComandante'

referenceFile=os.environ['HOME']+'/ShareTestResults/elComandante/P-A-2-23_ElComandanteTest_2015-07-13_15h33m_1436819615/000_FPIXTest_p17/commander_FPIXTest.root'
IVReferenceFile=os.environ['HOME']+'/ShareTestResults/elComandante/P-A-2-23_ElComandanteTest_2015-07-13_15h33m_1436819615/001_IV_p17/ivCurve.log'
#referenceFile='/Users/jstupak/CMS/pixel/ShareTestResults/elComandante/P-A-2-23_ElComandanteTest_2015-07-13_15h33m_1436819615/000_FPIXTest_p17/commander_FPIXTest.root'
#IVReferenceFile='/Users/jstupak/CMS/pixel/ShareTestResults/elComandante/P-A-2-23_ElComandanteTest_2015-07-13_15h33m_1436819615/001_IV_p17/ivCurve.log'

#outputDir=os.environ['HOME']+'/forExperts'

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

if len(argv)>1:
    testName=argv[1]
else:
    raise Exception("You must specify which test to check")

inputDirs=None
if len(argv)>2:
    inputDirs=argv[2:]

testFiles=[]; IVFiles=[]

if inputDirs:
    testFiles=[glob(d+'/*/commander_'+testName+'.root')[0] for d in inputDirs]
    if testName=='FPIXTest': IVFiles=[glob(d+'/*_IV_*/ivCurve.log')[0] for d in inputDirs]
else:
    for module in goodModuleNames:
        s=os.environ['HOME']+'/allTestResults/'+module+'_*/*_'+testName+'_*/commander_'+testName+'.root'
        try: testFiles.append(sorted(glob(s))[-1])
        except: 
            print 'Found no files matching:',s
            exit()

        if testName=='FPIXTest': 
            s=os.environ['HOME']+'/allTestResults/'+module+'_*/*_IV_*/ivCurve.log'
            try: IVFiles.append(sorted(glob(s))[-1])
            except:
                print 'Found no files matching:',s
                exit()

if testName=='Pretest':
    theComparisons=[Comparison('Pretest/programROC_V0',testFiles,'Pretest/programROC_V0',referenceFile,'deltaVana vs ROC: All deltaVana values should be significantly greater than 0. Small values indicate an inability to program the ROC.'),
                    Comparison('Pretest/Iana_V0',testFiles,'Pretest/Iana_V0',referenceFile,'Iana vs ROC: All Iana values should be approximately 24. Values significantly different from 24 indicate an issue with the analog voltage.'),
                    Comparison('HA',testFiles,'HA',referenceFile,'Iana vs time: All Iana values should be about 0.38. Iana is sampled periodically throughtout the test, so it is okay to have large gaps along the x-axis.'), 
                    Comparison('HD',testFiles,'HD',referenceFile,'Idig vs time: All Idig values should be about 0.45. Idig is sampled periodically throughtout the test, so it is okay to have large gaps along the x-axis.')]
    theComparisons+=[Comparison('Pretest/pretestVthrCompCalDel_c*r*_C'+str(i)+'_V0',testFiles,'Pretest/pretestVthrCompCalDel_c*_r*_C0_V0',referenceFile,'VthrComp vs CalDel: All plots should have the same tornado-esque shape as the reference plot, and a black dot should be located somewhere near the center.') for i in range(16)]

if testName=='FPIXTest':
    theComparisons=[]
    theComparisons+=[Comparison('IV/IV',IVFiles,'IV/IV',IVReferenceFile,'I vs V: Current at 150V should not exceed 2uA and the ratio of current at 150V and 100V should not exceed 2.')]
    #theComparisons+=[Comparison('Trim/dist_thr_TrimThrFinal_vcal_C'+str(i)+'_V0',testFiles,'Trim/dist_thr_TrimThrFinal_vcal_C0_V0',referenceFile,'Distribution should be sharply peaked around 35') for i in range(16)]
    theComparisons+=[Comparison('Scurves/dist_thr_scurveVcal_Vcal_C'+str(i)+'_V0',testFiles,'Scurves/dist_thr_scurveVcal_Vcal_C0_V0',referenceFile,'VCal turn-on threshold: Distribution should be sharply peaked around 35, as we have trimmed to this value.') for i in range(16)]
    theComparisons+=[Comparison('Scurves/dist_sig_scurveVcal_Vcal_C'+str(i)+'_V0',testFiles,'Scurves/dist_sig_scurveVcal_Vcal_C0_V0',referenceFile,'VCal turn-on width: Distribution should peak at or below ~3. The width is an indication of the noise present.') for i in range(16)]
    theComparisons+=[Comparison('PhOptimization/PH_c*_r*_C'+str(i)+'_V0',testFiles,'PhOptimization/PH_c*_r*_C0_V0',referenceFile,'Pulse height vs Vcal: Pulse height should be ~40 (250) at a Vcal of 0 (100), and linear in between.') for i in range(16)]
    theComparisons+=[Comparison('GainPedestal/gainPedestalNonLinearity_C'+str(i)+'_V0',testFiles,'GainPedestal/gainPedestalNonLinearity_C0_V0',referenceFile,'Pulse height non-linearity: Distribution should be sharply peaked just below 1. Smaller values indicate a non-linear pixel response.') for i in range(16)]
    theComparisons+=[Comparison('PixelAlive/PixelAlive_C'+str(i)+'_V0',testFiles,'PixelAlive/PixelAlive_C0_V0',referenceFile,'Pixel Alive: Good pixels are shown as red. At least ~95% of all pixels should be red.') for i in range(16)]
    theComparisons+=[Comparison('BB3/dist_rescaledThr_C'+str(i)+'_V0',testFiles,'BB3/dist_rescaledThr_C0_V0',referenceFile,'Adjusted VthrComp threshold in units of sigma: At least ~95% of all entries should have x values less than 5.') for i in range(16)]
    
################################################################
################################################################
################################################################

if __name__=='__main__':

    results=[]
    i=0
    badModules=[]
    while i<len(theComparisons):
        #gSystem.Sleep(100)
        result=theComparisons[i].do()
        
        #go back one test
        if result==-1: i=max(i-1,0)

        if type(result)==type([]):
            try: results[i]=result
            except: results.append(result)
            i+=1

    badModules=set([])
    for result in results:
        badModules=badModules|set(result)
    badModules=list(badModules)

#  5-31-16: comment out instructions to swap out non-perfect modules - Jamie 
#    if testName=='Pretest':
#        if len(badModules)>0:
#            print 'Replace the following module(s) and repeat the pre-test:'
#            for m in badModules:
#                print '    - '+str(m)
#        else:
#            print 'All modules are good.  Continue to the next test.\n\n'

