#! /usr/bin/env python

"""
Author: John Stupak (jstupak@fnal.gov)
Date: 5-2-15
Usage: ./checkPretest.py <input dir>
"""

import ROOT
#ROOT.gErrorIgnoreLevel = ROOT.kWarning
from ROOT import *
gStyle.SetOptStat(0)
import math
import os
from config import *
from fnmatch import fnmatch

c=TCanvas('c','',1000,850)
refPad=TPad('refPad','Reference Plot',.666,0,1,.5)
refPad.Draw()

textPad=TPad('textPad','',.666,.5,1,1)
textPad.Draw()

testPad=TPad('testPad','',0,0,.666,1)
testPad.Divide(2,2)
testPad.Draw()

################################################################
################################################################
################################################################

goodModules=[]

def click(moduleNo):

    global goodModules

    if gPad.GetEvent()==11:
        if moduleNo in goodModules:
            goodModules.remove(moduleNo)

            testPad.cd(moduleNo+1)
            gPad.SetFillColor(kRed)
            gPad.Modified()
            gPad.Update()
            
        else:
            goodModules+=[moduleNo]
            goodModules.sort()

            testPad.cd(moduleNo+1)
            gPad.SetFillColor(kGreen)
            gPad.Modified()
            gPad.Update()

    #else: print gPad.GetEvent()

    return None

def makeIV(input):
    """
    #
    #--------LOG from Tue 30 Jun 2015 at 14h:26m:49s ---------
    #
    #voltage(V)current(A)timestamp
    -0.030-1.6675e-081435692186
    -5.028-5.0295e-081435692191
    -10.026-7.5020e-081435692196
    -15.023-9.8705e-081435692201
    """

    values=[]
    for line in open(input):
        if line[0]=='#': continue
        values.append([abs(float(line.split()[0])),float(line.split()[1])])
    
    nBins=len(values)
    xMin=0
    xMax=nBins*round(values[1][0]-xMin,0)
    binWidth=float(xMax-xMin)/nBins
    xMin-=binWidth/2
    xMax-=binWidth/2
    
    h=TH1F('IV','IV;-U [V];-I [#muA]',nBins,xMin,xMax)
    for i in range(len(values)): h.SetBinContent(i+1, -1E6*values[i][1])
    h.SetMaximum(10*h.GetMaximum())
    
    return h

################################################################
################################################################
################################################################

class Comparison:
    
    def __init__(self, hName, testFiles, refName, referenceFile, info='All plots should resemble the reference plot'):
        self.hName=hName
        self.testFiles=testFiles
        self.refFile=referenceFile
        #self.outputDir=outputDir
        self.info=info

        self.goodModuleNames=[f.split('_')[0].split('/')[-1] for f in self.testFiles]

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    
    def do(self):
        print self.hName

        if self.hName=='IV/IV':
            #make temporary root file and put IV plot in it
            testFiles=[]
            for f in self.testFiles:
                file=TFile(f.replace('log','root'),'RECREATE')
                file.cd()
                file.mkdir('IV')
                file.cd('IV')
                h=makeIV(f)
                file.Write()
                testFiles.append(file)
        else:
            testFiles=[TFile(f) for f in self.testFiles]

        nModules = len(self.testFiles)
        
        global goodModules
        goodModules=[]
        
        refPad.cd()

        if self.hName=='IV/IV':
            #make temporary root file and put IV plot in it
            file=TFile(self.refFile.replace('log','root'),'RECREATE')
            file.cd()
            file.mkdir('IV')
            file.cd('IV')
            h=makeIV(self.refFile)
            file.Write()
            self.refTFile=file
        else:
            self.refTFile=TFile(self.refFile)

        if self.hName=='IV/IV' or 'BB3' in self.hName: refPad.SetLogy()

        for k in self.refTFile.GetListOfKeys():
            dir=k.ReadObj()
            if fnmatch(dir.GetName(),self.hName.split('/')[-1]) and not 'IV' in self.hName:
                ref=dir.Clone('REF__'+self.hName.split('/')[-1])
                break
            if type(dir)!=type(TDirectoryFile()): continue
            for key in dir.GetListOfKeys():
                if fnmatch(key.GetName(),self.hName.split('/')[-1]):
                    ref=key.ReadObj().Clone('REF__'+self.hName.split('/')[-1])
                    break
        is2D=(type(ref)==type(TH2D()))
        ref.Draw('COLZ'*is2D)

        if 'programROC_V0' in self.hName: ref.SetMinimum(0)
        if 'HA' in self.hName:
            ref.SetTitle('Iana vs time')
            ref.SetMaximum(0.5)
        if 'HD'in self.hName:
            ref.SetTitle('Idig vs time')
            ref.SetMaximum(0.7)
        if 'thr_scurveVcal_Vcal' in self.hName:
            #ref.GetXaxis().SetRangeUser(15,55)
            pass
        if 'Scurves/dist' in self.hName or 'gainPedestalNonLinearity' in self.hName:
            gStyle.SetOptStat(1)
        else:
            gStyle.SetOptStat(0)
            
        textPad.cd()

        wordsPerLine=5
        height=0.1*len(self.info.split())/wordsPerLine
        text=TPaveText(.1,.9-min(height,0.8),.9,.9,"NB")
        text.SetFillColor(kWhite)
        text.SetTextAlign(13)
   
        t=[]
        line=[]
        for word in self.info.split():
            if len(line)>=wordsPerLine: 
                t.append(line)
                line=[word]
            else:
                line.append(word)
        t.append(line)

        for line in t:
            text.AddText(' '.join(line))
        text.Draw()

        c.cd()

        histograms=[]
        for i in range(nModules):
            testPad.cd(i+1)
            gPad.SetFillColor(kWhite)
            gPad.Modified()
            gPad.Update()

            if self.hName=='IV/IV' or 'BB3' in self.hName: gPad.SetLogy()

            h=None

            for k in testFiles[i].GetListOfKeys():
                dir=k.ReadObj()
                if fnmatch(dir.GetName(),self.hName.split('/')[-1]) and not 'IV' in self.hName:
                    h=dir.Clone(self.hName.split('/')[-1])
                    break
                if type(dir)!=type(TDirectoryFile()): continue
                for key in dir.GetListOfKeys():
                    if fnmatch(key.GetName(),self.hName.split('/')[-1]):
                        h=key.ReadObj().Clone()
                        break

            try:
                h.SetTitle(self.goodModuleNames[i]+': '+h.GetTitle())
                gPad.SetFillColor(kWhite)
                gPad.Modified()
                gPad.Update()
                h.Draw('COLZ'*is2D)
                histograms.append(h)

                if 'programROC_V0' in self.hName: h.SetMinimum(0)
                if 'HA' in self.hName:
                    h.SetTitle(self.goodModuleNames[i]+': Iana vs time')
                    h.SetMaximum(0.5)
                if 'HD'in self.hName:
                    h.SetTitle(self.goodModuleNames[i]+': Idig vs time')
                    h.SetMaximum(0.7)                    
                if 'thr_scurveVcal_Vcal' in self.hName:
                    #h.GetXaxis().SetRangeUser(15,55)
                    pass

                if self.hName=='IV/IV':
                    I100=h.GetBinContent(h.FindBin(100))
                    I150=h.GetBinContent(h.FindBin(150))

                    l=TLatex()
                    #l.DrawLatexNDC(.15,.85,"I(150V)="+str(round(I150,2))+"#muA")
                    l2=TLatex()
                    #l2.DrawLatexNDC(.15,.8,"I(150V)/I(100V)="+str(round(I150/I100,2)))

                gPad.SetFillColor(kWhite)
                gPad.Modified()
                gPad.Update()
                gPad.SetFillColor(kRed)
                gPad.Modified()
                gPad.Update()

                if gPad.GetListOfExecs().GetSize()==0: gPad.AddExec('exec','TPython::Exec( "click('+str(i)+')" );')
            except: 
                print 'Missing plot for module',self.goodModuleNames[i]

        '''
        b='foo'
        while b:
            b=raw_input()
            exec(b)
                
        gPad.Modified()
        gPad.Update()
        '''

        while True:
            input=raw_input(8*'\n'+self.info+'\n\n'+'Press enter to submit results.\n'+'Enter "-1" to go back a test.\n\n')
            if input=='-1': 
                #refPad.Close()
                #testPad.Close()
                #c.Close()
                return -1

            if input=='':
                badModules=[x for x in range(nModules) if x not in goodModules]
                for i in badModules:
                    try: 
                        gROOT.SetBatch(True)
                        c2=TCanvas()
                        if self.hName=='IV/IV' or 'BB3' in self.hName: c2.SetLogy()
                        is2D=(type(histograms[i])==type(TH2D()))
                        histograms[i].Draw('COLZ'*is2D)

                        debugDir=os.path.dirname(self.testFiles[i])+'/debug'
                        if not os.path.isdir(debugDir): os.makedirs(debugDir)
                        c2.SaveAs(debugDir+'/'+histograms[i].GetName()+'.pdf')
                        gROOT.SetBatch(False)
                    except: pass
                badModuleNames=[self.goodModuleNames[i] for i in badModules]

                #for i in range(nModules):
                #    testPad.cd(i+1)
                #refPad.Close()
                #testPad.Close()
                #c.Close()

                if self.hName=='IV/IV' or 'BB3' in self.hName:
                    for i in range(nModules):
                        testPad.cd(i+1)
                        gPad.SetLogy(False)
                    refPad.SetLogy(False)
                        

                return badModuleNames
