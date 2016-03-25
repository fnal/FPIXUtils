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

#if len(sys.argv)<2:
    #inputFile='/Users/jstupak/tmp/P-A-3-42.root'
#else:
inputFile=sys.argv[1]

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

def analyze(inputFile, outputDir):


    slope = range(16) 
    offset = range(16)
    low_eff_hr = range(16)
    low_eff_lr = range(16)
    unif_high = range(16)
    unif_low = range(16)

    qfile = open("SummaryQPlots_"+inputFile+".txt",'r')
    #qfile = open("SummaryQplots.txt")
    line = qfile.readlines()
    for l in range(2,len(line)):
       values = string.split(line[l])
#       slope[l-2] = values[1]+values[2]+values[3]
#       offset[l-2] = values[4]+values[5]+values[6].strip('\n')
       slope[l-2] = float(values[1])
       offset[l-2] = float(values[4])
    
    low98 = []
    low95 = []
    eff_unif_file = open('hrEfficiency.log', 'r')
    eff_unif_lines = eff_unif_file.readlines()
    for line in eff_unif_lines:
        for i in xrange(0,16):
            if 'Lowesest DC Eff at High Rate for  ROC:'+str(i) in line:
                words_low_eff_hr = string.split(line)
                low_eff_hr[i] = float(words_low_eff_hr[11])
                  
            elif 'Lowest DC Eff at Low Rate for  ROC:'+str(i) in line:
                words_low_eff_lr = string.split(line)
                low_eff_lr[i] = float(words_low_eff_lr[11])
            elif 'Highest  DC Uni  for  ROC:'+str(i) in line:
                words_unif_high = string.split(line)
                unif_high[i] = float(words_unif_high[8])
            elif 'Lowest DC Uni for  ROC:'+str(i) in line:
                words_unif_low = string.split(line)
                unif_low[i] = float(words_unif_low[8])
        if 'Number DC <= 98% :' in line:
            print line
            n98s =string.split(line)[5]
            print n98s
            n98 = n98s.replace(':','')     
        elif 'Number DC <= 95% :' in line:
            print line
            n95s =string.split(line)[5]
            print n95s
            n95 = n95s.replace(':','')
    testtime = SE(top, 'TIME')
    testtime.text = str(datetime.now()) 
  


    test = SE(top, 'TEST')
    attachName(test)
    
    n98val = SE(test,'DC_BELOW_98')
    n98val.text=str(n98)
    n95val = SE(test,'DC_BELOW_95')
    n95val.text=str(n95)
    xraytested = SE(test,'XRAY_TESTED')
    xraytested.text=str(1)

    rocs=SE(test, 'ROCS')

    for i in range(16):
        roc=SE(rocs, 'ROC')
        position=SE(roc, 'POSITION')
        position.text=str(i)
        xray_offset=SE(roc, 'XRAY_OFFSET')
        xray_offset.text=str(offset[i])
        xray_slope=SE(roc, 'XRAY_SLOPE')
        xray_slope.text=str(slope[i])
        xray_low_eff_hr=SE(roc, 'LOW_DC_HIGHRATE_EFF')
        xray_low_eff_hr.text=str(round(low_eff_hr[i],3))
        xray_low_eff_lr=SE(roc,'LOW_DC_LOWRATE_EFF')
        xray_low_eff_lr.text=str(round(low_eff_lr[i],3))
        xray_unif_low=SE(roc,'LOW_DC_UNI')
        xray_unif_low.text=str(round(unif_low[i],3))
        xray_unif_high=SE(roc,'HIGH_DC_UNI')
        xray_unif_high.text=str(round(unif_high[i],3))

    for i in range(16):
    	pic=SE(top, 'PIC')
    	attachName(pic)
    	file=SE(pic, 'FILE')
    	file.text='Qplot_'+inputFile+'_C' + str(i) +'.png'
        part=SE(pic,'PART')
        part.text='sidet_p'

    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='Results_Hr_Eff_'+inputFile+'.png'
    part=SE(pic,'PART')
    part.text='sidet_p'

    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='Results_Hr_Rate_by_DCol_'+inputFile+'.png'
    part=SE(pic,'PART')
    part.text='sidet_p'
    
    pic=SE(top, 'PIC')
    attachName(pic)
    file=SE(pic, 'FILE')
    file.text='Results_Hr_DC_Uniformity_'+inputFile+'.png'
    part=SE(pic,'PART')
    part.text='sidet_p'


################################################################

def makeXML(inputFile):
    
    global moduleName
    moduleName = string.upper(inputFile[0]+'-'+inputFile[1]+'-'+inputFile[2]+'-'+inputFile[3:5])

    global outputDir
    outputDir+='/'+inputFile
    if os.path.exists(outputDir):
        print 'WARNING: outputDir exists'
        #exit()
    else:
        print outputDir
        os.makedirs(outputDir)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    global top
    top=Element('ROOT')
    top.set('xmlns:xsi','http://www.w3.org/2001/XMLSchema-instance')

    analyze(inputFile, outputDir)
        
    output=open(outputDir+'/master.xml','w')
    output.write(prettify(top))
    output.close()

    #print
    #print prettify(top)
    #print

    os.system ("cp %s %s" % ("Results_Hr_DC_Uniformity_"+inputFile+ ".png", outputDir))
    os.system ("cp %s %s" % ("Results_Hr_Eff_"+inputFile+ ".png", outputDir))
    os.system ("cp %s %s" % ("Results_Hr_Rate*.png", outputDir))
    os.system ("cp %s %s" % ("Qplot_*.png", outputDir))

    os.chdir(outputDir)
    zip=zipfile.ZipFile('../'+moduleName+'.zip', mode='w')
    for file in glob('*'):
        zip.write(file)
    zip.close()

################################################################
################################################################
################################################################

if __name__=='__main__':
    xml=makeXML(inputFile)
