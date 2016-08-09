#! /usr/bin/env python

"""
Author: John Stupak (jstupak@fnal.gov)
Date: 4-9-15
Usage: python dbUpload.py <input dir>
"""

DEBUG=False
dacsOnly=False
makePlots=True

from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from xml.dom import minidom
SE=SubElement

import ROOT
#if not DEBUG: 
ROOT.gErrorIgnoreLevel = ROOT.kWarning
from ROOT import *
gStyle.SetOptStat(0)
gROOT.SetBatch(1)

from moduleSummaryPlottingTools import *

from glob import glob
import os
import subprocess
import sys
import zipfile
from shutil import rmtree

if len(sys.argv)<2:
    inputDir='/Users/jstupak/CMS/pixel/ShareTestResults/M_FR_902_ElComandanteTest_2015-04-16_15h24m_1429215874'
else:
    inputDir=sys.argv[1].rstrip('/')

################################################################
################################################################
################################################################

def prettify(elem):
    roughString = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(roughString)
    return reparsed.toprettyxml(indent="  ")

#---------------------------------------------------------------

def attachName(parent):
    name=SE(parent,'NAME')
    name.text=moduleName

################################################################

def getHAHDPlot(f, outputDir):

    h=f.Get('HA')
    
    c=TCanvas()
    h.Draw()
    c.SaveAs(outputDir+'/HA.png')

    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='HA.png'
    part=SE(pic,'PART')
    part.text='sidet_p'


    h=f.Get('HD')
    
    c=TCanvas()
    h.Draw()
    c.SaveAs(outputDir+'/HD.png')

    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='HD.png'
    part=SE(pic,'PART')
    part.text='sidet_p'


def getProgramROCPlot(f, deadROCs, outputDir):
    h=f.Get('Pretest/programROC_V0')
    
    c=TCanvas()
    h.Draw()
    c.SaveAs(outputDir+'/programROC.png')

    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='programROCs.png'
    txt=SE(pic, 'TXT')
    txt.text='programROC.txt'
    part=SE(pic,'PART')
    part.text='sidet_p'

    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('\ndeadROCs='+str(deadROCs)+'\n')
    
#---------------------------------------------------------------

def getVthrCompCalDelPlot(f, CalDels, VthrComps, outputDir):
    
    c=TCanvas()
    for key in f.Get('Pretest').GetListOfKeys():
        if 'pretestVthrCompCalDel' in key.GetName():
            key.ReadObj().Draw('colz')
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')

            pic=SE(top, 'PIC')
            attachName(pic)
            file=SE(pic, 'FILE')
            file.text=key.GetName()+'.png'
            txt=SE(pic, 'TXT')
            txt.text=key.GetName()+'.txt'
            part=SE(pic,'PART')
            part.text='sidet_p'

            comment=open(outputDir+'/'+txt.text,'w')
            n=int(key.GetName().split('_')[3][1:])
            comment.write('\nVthrComp='+str(VthrComps[n])+', CalDel='+str(CalDels[n])+'\n')

#---------------------------------------------------------------
    
def getVanaPlot(f, outputDir):
        
    h=f.Get('Pretest/VanaSettings_V0')
    c=TCanvas()
    h.Draw()
    c.SaveAs(outputDir+'/Vana.png')
    
    pic=SE(top,'PIC')
    attachName(pic)
    file=SE(pic,'FILE')
    file.text='Vana.png'
    part=SE(pic,'PART')
    part.text='sidet_p'
    
    Vana=[]
    for binNo in range(1,h.GetNbinsX()+1):
        V=int(h.GetBinContent(binNo))
        Vana.append(V)
    txt=SE(pic,'TXT')
    txt.text='Vana.txt'
    
    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('\nVana='+str(Vana)+'\n')

#---------------------------------------------------------------

def getIanaPlot(f, outputDir):    

    h=f.Get('Pretest/Iana_V0')
    c=TCanvas()
    h.Draw()
    c.SaveAs(outputDir+'/Iana.png')

    pic=SE(top,'PIC')
    attachName(pic)
    file=SE(pic,'FILE')
    file.text='Iana.png'
    part=SE(pic,'PART')
    part.text='sidet_p'

    Iana=[]
    for binNo in range(1,h.GetNbinsX()+1):
        I=round(float(h.GetBinContent(binNo)),1)
        Iana.append(I)
    txt=SE(pic,'TXT')
    txt.text='Iana.txt'
    
    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('\nIana='+str(Iana)+'\n')

#---------------------------------------------------------------

def getPixelAlivePlots(f, nDeadPixels, nMaskDefectPixels, nAddressDefectPixels, outputDir):

    c=TCanvas()
    for key in f.Get('PixelAlive').GetListOfKeys():
        if 'PixelAlive_C' in key.GetName():
            h=key.ReadObj()
            h.Draw('colz')
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')
            n=int(key.GetName().split('_')[1][1:])

            deadPixels=[]
            for xBin in range(1,h.GetNbinsX()+1):
                for yBin in range(1,h.GetNbinsY()+1):
                    if h.GetBinContent(xBin, yBin)<1: deadPixels.append([xBin-1,yBin-1])

            if len(deadPixels)!=nDeadPixels[n]:
                print 'ERROR: Wrong number of dead pixels found'
                print '       From pXar log:', nDeadPixels[n]
                print '       From root file:',len(deadPixels)
                exit()

            defectivePixels.append(deadPixels)

            # - - - - - - - - - - - - - - - - - - - - - - - - -

            h=f.Get('PixelAlive/'+h.GetName().replace('PixelAlive','MaskTest'))
            h.Draw('colz')
            c.SaveAs(outputDir+'/'+h.GetName()+'.png')
            n=int(h.GetName().split('_')[1][1:])

            maskDefectPixels=[]
            for xBin in range(1,h.GetNbinsX()+1):
                for yBin in range(1,h.GetNbinsY()+1):
                    if [xBin-1,yBin-1] in deadPixels: continue
                    if h.GetBinContent(xBin, yBin)<0: 
                        maskDefectPixels.append([xBin-1,yBin-1])
                        defectivePixels[n].append([xBin-1,yBin-1])
                                                
            if len(maskDefectPixels)!=nMaskDefectPixels[n]:
                print 'ERROR: Wrong number of un-maskable pixels found'
                print '       From pXar log:', nMaskDefectPixels[n]
                print '       From root file:',len(maskDefectPixels)
                exit()

            # - - - - - - - - - - - - - - - - - - - - - - - - -   

            h=f.Get('PixelAlive/'+h.GetName().replace('MaskTest','AddressDecodingTest'))
            h.Draw('colz')
            c.SaveAs(outputDir+'/'+h.GetName()+'.png')
            n=int(h.GetName().split('_')[1][1:])

            addressDefectPixels=[]
            for xBin in range(1,h.GetNbinsX()+1):
                for yBin in range(1,h.GetNbinsY()+1):
                    if [xBin-1,yBin-1] in deadPixels: continue
                    if h.GetBinContent(xBin, yBin)<0: 
                        addressDefectPixels.append([xBin-1,yBin-1])
                        defectivePixels[n].append([xBin-1,yBin-1])

            if len(addressDefectPixels)!=nAddressDefectPixels[n]:
                print 'ERROR: Wrong number of un-addressable pixels found'
                print '       From pXar log:', nAddressDefectPixels[n]
                print '       From root file:',len(addressDefectPixels)
                exit()

#---------------------------------------------------------------

#def getBumpBondingPlots(f, badBumpsFromLog, bbCuts, outputDir):
def getBumpBondingPlots(f, outputDir):

    c=TCanvas()

    for key in f.Get('BB3').GetListOfKeys():

        if 'dist_rescaledThr_C' in key.GetName():
            if makePlots:
                c.SetLogy(True)
                key.ReadObj().Draw()
                c.SaveAs(outputDir+'/'+key.GetName()+'.png')
                c.SetLogy(False)

                pic=SE(top, 'PIC')
                attachName(pic)
                file=SE(pic, 'FILE')
                file.text=key.GetName()+'.png'
                part=SE(pic,'PART')
                part.text='sidet_p'

        # - - - - - - - - - - - - - - - - - - - - - - - - -
        
        elif 'rescaledThr_C' in key.GetName():
            h=key.ReadObj()
            h.Draw('colz')
            c.SaveAs(outputDir+'/'+key.GetName()+'.png')
            n=int(key.GetName().split('_')[1][1:])

            badBumps.append([])
            for xBin in range(1, h.GetNbinsX()+1):
                for yBin in range(1, h.GetNbinsY()+1):
                    if h.GetBinContent(xBin,yBin)>=5:
                        pix=[xBin-1,yBin-1]
                        if pix not in defectivePixels[n]:                                                                                                                                              
                            badBumps[n].append(pix)
                            defectivePixels[n].append(pix)
            
#---------------------------------------------------------------

def getSCurvePlots(f, outputDir):
    
    goodPlots=['adjustVcal_C',
               'thr_scurveVthrComp_VthrComp_C','sig_scurveVthrComp_VthrComp_C','thn_scurveVthrComp_VthrComp_C',
               'thr_scurveVcal_Vcal_C','sig_scurveVcal_Vcal_C',
               ]

    c=TCanvas()
    for key in f.Get('Scurves').GetListOfKeys():
        if makePlots:
            for plot in goodPlots:
                if plot in key.GetName():
                    if 'dist' in key.GetName(): key.ReadObj().Draw()
                    else: key.ReadObj().Draw('COLZ')
                    c.SaveAs(outputDir+'/'+key.GetName()+'.png')

                    is2D=(type(key.ReadObj())==type(TH2D()))
                    if not is2D:
                        pic=SE(top, 'PIC')
                        attachName(pic)
                        file=SE(pic, 'FILE')
                        file.text=key.GetName()+'.png'
                        part=SE(pic,'PART')
                        part.text='sidet_p'

        #get pixels which can't be trimmed
        if key.GetName().startswith('thr_scurveVcal_Vcal_C'):
            h=key.ReadObj()
            n=int(key.GetName().split('_')[3][1:])

            trimDefectPixels.append([])

            for xBin in range(1,h.GetNbinsX()+1):
                for yBin in range(1,h.GetNbinsY()+1):
                    if h.GetBinContent(xBin, yBin)<25 or h.GetBinContent(xBin, yBin)>45: 
                        pix=[xBin-1,yBin-1]
                        if pix not in defectivePixels[n]:
                            trimDefectPixels[n].append(pix)
                            defectivePixels[n].append(pix)

#---------------------------------------------------------------

def getTrimPlots(f, outputDir):
    if not makePlots: return

    goodPlots=['dist_TrimMap_C',
               ]

    c=TCanvas()
    for key in f.Get('Trim').GetListOfKeys():
        for plot in goodPlots:
            if plot in key.GetName():
                if 'dist' in key.GetName(): key.ReadObj().Draw()
                else: key.ReadObj().Draw('COLZ')
                c.SaveAs(outputDir+'/'+key.GetName()+'.png')

                is2D=(type(key.ReadObj())==type(TH2D()))
                if not is2D:
                    pic=SE(top, 'PIC')
                    attachName(pic)
                    file=SE(pic, 'FILE')
                    file.text=key.GetName()+'.png'
                    part=SE(pic,'PART')
                    part.text='sidet_p'

#---------------------------------------------------------------

def getPulseHeightOptPlots(f, outputDir):
    if not makePlots: return

    goodPlots=['dist_PH_mapHiVcal_C',
               'dist_PH_mapLowVcal_C']

    c=TCanvas()
    for key in f.Get('PhOptimization').GetListOfKeys():
        for plot in goodPlots:
            if plot in key.GetName():
                if 'dist' in key.GetName(): key.ReadObj().Draw()
                else: key.ReadObj().Draw('COLZ')
                c.SaveAs(outputDir+'/'+key.GetName()+'.png')

                is2D=(type(key.ReadObj())==type(TH2D()))
                if not is2D:
                    pic=SE(top, 'PIC')
                    attachName(pic)
                    file=SE(pic, 'FILE')
                    file.text=key.GetName()+'.png'
                    part=SE(pic,'PART')
                    part.text='sidet_p'

#---------------------------------------------------------------

def getGainPedestalPlots(f,outputDir):
    if not makePlots: return

    goodPlots=['gainPedestalNonLinearity',
               ]

    c=TCanvas()
    for key in f.Get('GainPedestal').GetListOfKeys():
        for plot in goodPlots:
            if plot in key.GetName():
                key.ReadObj().Draw()
                c.SaveAs(outputDir+'/'+key.GetName()+'.png')

                pic=SE(top, 'PIC')
                attachName(pic)
                file=SE(pic, 'FILE')
                file.text=key.GetName()+'.png'
                part=SE(pic,'PART')
                part.text='sidet_p'

################################################################

def makeSummaryPlots(inputDir, outputDir, log, data):
    if not makePlots: return

    data=TFile(data['fulltest'])

    produceLessWebSummaryPlot(data,'BB3/rescaledThr',outputDir,zRange=(-5,5), isBB3=True, moduleName = moduleName)
    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='BB3_rescaledThr.png'
    part=SE(pic,'PART')
    part.text='sidet_p'
    txt=SE(pic,'TXT')
    txt.text=file.text.replace('png','txt')
    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('\n'+file.text.split('.')[0])
    
    for hist in ['PixelAlive/PixelAlive','PixelAlive/MaskTest','PixelAlive/AddressDecodingTest',
                 'PhOptimization/PH_mapLowVcal','PhOptimization/PH_mapHiVcal',
                 'Scurves/sig_scurveVcal_Vcal','Scurves/thr_scurveVcal_Vcal',
                 ]:

        produceLessWebSummaryPlot(data,hist,outputDir, moduleName = moduleName)
        pic=SE(top, 'PIC')
        attachName(pic)
        file=SE(pic, 'FILE')
        file.text=hist.replace('/','_')+'.png'
        part=SE(pic,'PART')
        part.text='sidet_p'
        txt=SE(pic,'TXT')
        txt.text=file.text.replace('png','txt')
        comment=open(outputDir+'/'+txt.text,'w')
        comment.write('\n'+file.text.split('.')[0])

    produceLessWebSummaryPlot(data,'Trim/TrimMap',outputDir,zRange=(0,15), moduleName = moduleName)
    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='Trim_TrimMap.png'
    part=SE(pic,'PART')
    part.text='sidet_p'
    txt=SE(pic,'TXT')
    txt.text=file.text.replace('png','txt')
    comment=open(outputDir+'/'+txt.text,'w')
    comment.write('\n'+file.text.split('.')[0])

################################################################

def analyzePreTest(inputDir, outputDir, log, data):
    log=log['pretest']
    data=TFile(data['pretest'])

    f=iter(open(log,'r'))

    canTime=True
    for line in f:

        if 'INFO: TBM phases:  160MHz:' in line:
            if '-1' in line: canTime=False

        if 'ROCs are all programmable' in line: deadROCs=[]
        elif 'cannot be programmed! Error' in line: deadROCs=[int(i) for i in line[line.find('ROCs')+len('ROCs'):line.find('cannot')].split()]
    
        if 'PixTestPretest::setVthrCompCalDel() done' in line:
            line=next(f)
            calDels=[int(i) for i in line.replace('_','').split('CalDel:')[1].split()]
            line=next(f)
            VthrComps=[int(i) for i in line.replace('_','').split('VthrComp:')[1].split()]

    ct=SE(test,'CAN_TIME')
    ct.text=str(int(canTime))

    if makePlots:
        getHAHDPlot(data, outputDir)
        getProgramROCPlot(data, deadROCs, outputDir)
        getVanaPlot(data, outputDir)
        getIanaPlot(data, outputDir)
        getVthrCompCalDelPlot(data, calDels, VthrComps, outputDir)
        
################################################################

def analyzeIV(inputDir, outputDir, log, data):
    inputName=glob(inputDir+'/*_IV_*/ivCurve.log')[0]
    input=open(inputName, 'r')
    outputName=outputDir+'/'+moduleName+'_IV.xml'
    output=open(outputName,'w')

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #scan header
    
    t=Element('ROOT')
    t.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')

    header=SE(t,'HEADER')
    type=SE(header,'TYPE')

    extension_table_name=SE(type,'EXTENSION_TABLE_NAME')
    extension_table_name.text='PH1_FPIX_ASSEMBLED_IV'
    name=SE(type,'NAME')
    name.text='Ph1 FNAL assembled module IV Test Data'

    run=SE(header,'RUN')
    run_name=SE(run,'RUN_NAME')
    run_name.text='Ph1 FNAL assembled module '+moduleName+' IV'

    run_begin_timestamp=SE(run,'RUN_BEGIN_TIMESTAMP')

    for line in input:
        if 'LOG from' in line:
            run_begin_timestamp.text=' '.join(line.split()[2:-1])
            break

    location=SE(run,'LOCATION')
    location.text='FNAL'
    comment_description=SE(run,'COMMENT_DESCRIPTION')
    comment_description.text=run_name.text

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #scan data

    data_set=SE(t,'DATA_SET')
    part=SE(data_set,'PART')
    serial_number=SE(part,'SERIAL_NUMBER')
    serial_number.text=moduleName
    kind_of_part=SE(part,'KIND_OF_PART')
    kind_of_part.text='Ph1 FPix 2x8 Sensor'

    values=[]
    for line in input:
        if line[0]=='#': continue
        data=SE(data_set,'DATA')
        voltage_volt=SE(data,'VOLTAGE_VOLT')
        voltage_volt.text=str(abs(float(line.split()[0])))
        tot_current_amp=SE(data,'TOT_CURRENT_AMP')
        tot_current_amp.text=str(abs(float(line.split()[1])))

        values.append([abs(float(line.split()[0])),float(line.split()[1])])

    output.write(prettify(t))
    output.close()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #main xml content

    scan=SE(top,'SCAN')
    attachName(scan)
    level=SE(scan,'LEVEL')
    if doCold: level.text='FNAL'
    else: level.text='FNAL_17C'
    type=SE(scan,'TYPE')
    type.text='IV'
    file=SE(scan,'FILE')
    file.text=os.path.basename(outputName)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    #until DB has field, upload the png
    
    nBins=len(values)
    xMin=0
    xMax=nBins*round(values[1][0]-xMin,0)
    binWidth=float(xMax-xMin)/nBins
    xMin-=binWidth/2
    xMax-=binWidth/2

    h=TH1F('IV',';-U [V];-I [#muA]',nBins,xMin,xMax)
    for i in range(len(values)): h.SetBinContent(i+1, -1E6*values[i][1])
    h.SetMaximum(5*h.GetMaximum())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    b=getBreakdown(h)
    breakdown=SE(scan,'BREAKDOWN')
    breakdown.text=str(round(b,1))

    c=getCompliance(values)
    compliance=SE(scan,'COMPLIANCE')
    compliance.text=str(round(c,1))
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    if doCold and makePlots:
        c=TCanvas()
        c.SetLogy()
        h.Draw()
        l=TLine(b,h.GetYaxis().GetXmin(),b,h.GetMaximum()); l.SetLineColor(kRed)
        l.Draw('same')
        c.SaveAs(outputName.replace('xml','png'))

        pic=SE(top,'PIC')
        attachName(pic)
        file=SE(pic,'FILE')
        file.text=os.path.basename(outputName.replace('xml','png'))
        txt=SE(pic,'TXT')
        txt.text=os.path.basename(outputName).replace('xml','txt')
        part=SE(pic,'PART')
        part.text='sidet_p'
        comment=open(outputDir+'/'+txt.text,'w')
        comment.write('\nbreakdown='+str(b)+'\n')

#---------------------------------------------------------------

def getBreakdown(h):

    tolerance=1./20000
    width=max(1,int(round(25./h.GetBinWidth(1),0)))
    
    h0=h.Clone('h0')

    lastFilledBin=0
    for binNo in range(1,h0.GetNbinsX()+1):
        if h0.GetBinContent(binNo)>0: lastFilledBin=binNo
        
        if h0.GetBinContent(binNo)<=0: h0.SetBinContent(binNo,0)
        else: h0.SetBinContent(binNo,log10(h0.GetBinContent(binNo)))
        
    h1=h0.Clone('h1')
    h1.Reset()
    for binNo in range(width+1,lastFilledBin-width):
        h1.SetBinContent(binNo,(h0.GetBinContent(binNo+width)-h0.GetBinContent(binNo-width))/(2*width*h0.GetBinWidth(binNo)))

    h2=h1.Clone('h2')
    h2.Reset()
    for binNo in range(width+2,lastFilledBin-width-1):
        h2.SetBinContent(binNo,(h1.GetBinContent(binNo+1)-h1.GetBinContent(binNo-1))/(2*h0.GetBinWidth(binNo)))

    if DEBUG:
        c_debug=TCanvas()
        h2.SetMinimum(-5*tolerance)
        h2.SetMaximum(5*tolerance)
        h2.Draw()
        l1=TLine(h2.GetXaxis().GetXmin(),tolerance,h2.GetXaxis().GetXmax(),tolerance); l1.Draw('same')
        l2=TLine(h2.GetXaxis().GetXmin(),-tolerance,h2.GetXaxis().GetXmax(),-tolerance); l2.Draw('same')
        c_debug.SaveAs('debug.pdf')

    above=False
    for binNo in range(lastFilledBin-width-1,width+2,-1):
        if h2.GetBinContent(binNo)>tolerance:
            above=True
        elif above:
            breakdown=h0.GetBinCenter(binNo+width+2)
            if DEBUG: print 'breakdown:',breakdown
            return breakdown

    return h0.GetXaxis().GetBinUpEdge(h0.GetNbinsX())

#---------------------------------------------------------------

def getCompliance(values):
    v=values[-1][0]
    i=values[-1][1]
        
    c=v

    if DEBUG: print 'compliance:',c
    
    return c

#---------------------------------------------------------------

def analyzeFullTest(inputDir, outputDir, log, data):

    log=log['fulltest']
    data=TFile(data['fulltest'])

    f=iter(open(log,'r'))
    for line in f:

        if 'ROCs are all programmable' in line: deadROCs=[]
        elif 'cannot be programmed! Error' in line: deadROCs=[int(i) for i in line[line.find('ROCs')+len('ROCs'):line.find('cannot')].split()]

        if 'number of dead pixels (per ROC)' in line:
            deadPixels=[int(x) for x in line.split()[-16:]]
            print 'deadPixels:',deadPixels

        if 'number of mask-defect pixels (per ROC)' in line:
            maskDefectPixels=[int(x) for x in line.split()[-16:]]
            print 'maskDefectPixels:',maskDefectPixels

        if 'number of address-decoding pixels (per ROC)' in line:
            addressDefectPixels=[int(x) for x in line.split()[-16:]]
            print 'addressDefectPixels:',addressDefectPixels

        if 'Final Module Temperature:' in line:
            finalTemp=line.split('Temperature:')[1].split()[0]
            print 'finalTemp:',finalTemp
            
        if 'Final Analog Current:' in line:
            finalIana=line.split('Current:')[1].strip()
            print 'finalIana:',finalIana

        if 'Final Digital Current:' in line:
            finalIdig=line.split('Current:')[1].strip()
            print 'finalIdig:',finalIdig

    try: deadPixels, maskDefectPixels, addressDefectPixels
    except: 
        print 'WARNING: Missing data - some subset of deadPixels, maskDefectPixels, addressDefectPixels'
        print deadPixels
        print maskDefectPixels 
        print addressDefectPixels

    RTD_TEMP=SE(test,'RTD_TEMP')
    RTD_TEMP.text=str(finalTemp)

    getPixelAlivePlots(data, deadPixels, maskDefectPixels, addressDefectPixels, outputDir)
    getTrimPlots(data,outputDir)
    getSCurvePlots(data,outputDir)
    getPulseHeightOptPlots(data,outputDir)
    getGainPedestalPlots(data,outputDir)
    getBumpBondingPlots(data, outputDir)

    global badBumps
    badBumps=[len(e) for e in badBumps]
    print 'badBumps:',badBumps

    global trimDefectPixels
    trimDefectPixels=[len(e) for e in trimDefectPixels]
    print 'trimDefectPixels:',trimDefectPixels

    try: deadROCs
    except:
        print 3*'\nWARNING'
        print 'No Pretest results found! Notfiy expert on call.'
        print 3*'WARNING\n'
        #exit()

    try: trimDefectPixels[15]
    except:
        trimDefectPixels=16*[4160]
        print 3*'\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        print 'No Scurves results found! Notfiy expert on call.'
        print 3*'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n'
        #exit()

    ROCS=SE(test,'ROCS')
    for i in range(16):
        ROC=SE(ROCS,'ROC')
        POSITION=SE(ROC,'POSITION')
        POSITION.text=str(i)
        IS_DEAD=SE(ROC,'IS_DEAD')
        IS_DEAD.text=str(int((i in deadROCs)))
        BADBUMPS_ELEC=SE(ROC,'BADBUMPS_ELEC')
        BADBUMPS_ELEC.text=str(badBumps[i])
        DEAD_PIX=SE(ROC,'DEAD_PIX')
        DEAD_PIX.text=str(deadPixels[i])
        UNMASKABLE_PIX=SE(ROC,'UNMASKABLE_PIX')
        UNMASKABLE_PIX.text=str(maskDefectPixels[i])
        UNADDRESSABLE_PIX=SE(ROC,'UNADDRESSABLE_PIX')
        UNADDRESSABLE_PIX.text=str(addressDefectPixels[i])
        VCAL_THRESH=SE(ROC,'VCAL_THRESH')
        VCAL_THRESH.text=str(trimDefectPixels[i])

#---------------------------------------------------------------

def getConfigs(inputDir, outputDir, log, data):
    if not makePlots: return

    for config in ['configParameters.dat', 
                   'tbParameters.dat', 
                   'tbmParameters_C*a.dat','tbmParameters_C*b.dat', 
                   'testParameters.dat', 
                   'testPatterns.dat', 
                   'defaultMaskFile.dat', 
                   'trimParameters35_C*.dat', 
                   'phCalibration_C*.dat', 
                   'phCalibrationFitErr35_C*.dat', 
                   'dacParameters35_C*.dat']:

        if len(glob(inputDir+'/*_FPIXTest_*/'+config))==0: 
            print 'WARNING: no config files found:', config
            #exit()

        for file in glob(inputDir+'/*_FPIXTest_*/'+config):
            subprocess.call(['cp', file, outputDir])
            
            c=SE(top,'CONFIG')

            attachName(c)
            f=SE(c,'FILE')
            f.text=os.path.basename(file)

################################################################

def makeXML(inputDir):
    
    global moduleName
    print 'inputDir:',inputDir
    print 
    moduleName=os.path.basename(inputDir.split('_')[0])
    print 'moduleName:',moduleName
    if len(moduleName)!=8:
	print 'Bad module name, aborting'
	return 
    global doCold
    doCold='m20C' in inputDir

    outputDir=os.environ['HOME']+'/dbUploads/'+moduleName
    if os.path.exists(outputDir):
        rmtree(outputDir)
    
    os.makedirs(outputDir)

    log={}
    data={}
    
    log['pretest']=inputDir+'/*_FPIXTest_*/commander_FPIXTest.log'
    data['pretest']=log['pretest'].replace('.log','.root')
    
    log['fulltest']=log['pretest'].replace('Pretest','FPIXTest')
    data['fulltest']=log['fulltest'].replace('.log','.root')
    
    log['iv']=inputDir+'/*_IV_*/ivCurve.log'
    
    for key in log.keys():
        try:
            log[key]=glob(log[key])[0]
            if key!='iv': data[key]=glob(data[key])[0]
        except:
            print 'Missing log:',key
            print

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    global top
    top=Element('ROOT')
    top.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')
    
    time=SE(top,'TIME')
    d=os.path.basename(inputDir).split('_')[-3]
    t=os.path.basename(inputDir).split('_')[-2]; t=t.replace('h',':').replace('m',':00')
    i=os.path.basename(inputDir).split('_')[-1]
    time.text=d+' '+t

    global test
    test=SE(top,'TEST')
    attachName(test)
    
    notes=SE(test,'NOTES')
    if makePlots:
        notes.text='Test results and config files can be found in: '+os.path.basename(inputDir)
    else:
        notes.text='Re-uploading new data from: '+os.path.basename(inputDir)

    process = subprocess.Popen(['grep', '-c', 'ERROR', log['fulltest']], stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    pxar_errors=SE(test,'PXAR_ERRORS')
    pxar_errors.text=stdout.strip()

    if doCold and makePlots and not dacsOnly: tests=[analyzeIV,
              makeSummaryPlots,
              analyzePreTest,
              analyzeFullTest,
              getConfigs,
              ]
    elif dacsOnly:
        tests=[getConfigs]
    else:
        tests=[analyzeIV]

    global defectivePixels, badBumps, trimDefectPixels
    defectivePixels=[]
    badBumps=[]
    trimDefectPixels=[]
    
    for f in tests:
        #try:
        f(inputDir, outputDir, log, data)
        #except Exception,e: 
        #print 'WARNING: unable to run',f.__name__
        #print str(e)

    output=open(outputDir+'/master.xml','w')
    output.write(prettify(top))
    output.close()

    #print
    #print prettify(top)
    #print

    os.chdir(outputDir)
    zip=zipfile.ZipFile('../'+moduleName+'.zip', mode='w')
    for file in glob('*'):
        zip.write(file)
    zip.close()

################################################################
################################################################
################################################################

if __name__=='__main__':
    xml=makeXML(inputDir)
