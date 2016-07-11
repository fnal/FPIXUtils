#!/usr/bin/env python
import argparse
import os
import csv

parser = argparse.ArgumentParser(description="Convert the calibration results in the Production Test Area to POS format for Jordan")
parser.add_argument("-c","--csv", dest="csv", default="", help="Input csv file")
parser.add_argument("-i","--input", dest="input", default="~/ProductionTestResults", help="Input directory")
parser.add_argument("-l","--list", dest="list", default="", help="Text file that contains a list of modules")
parser.add_argument("-o","--output", dest="output", default="POSFiles", help="Output directory for POS files")
parser.add_argument("-v","--verbose", dest="verbose", action="store_true", default=False, help="Enable Verbose Output")
parser.add_argument("-t","--temperature", dest="temp", default="m20", help="m20 or p17")
args = parser.parse_args()

if not os.path.isdir(args.input):
    print "Error! Input direcort "+args.input+" not found!"
    exit(1)

if not os.path.isdir(args.output): os.mkdir(args.output)

workingdir = os.getcwd()
inputdir = os.path.abspath(args.input)
outputdir = os.path.abspath(args.output)

selectedmodules = []
modulemap = {}

if args.csv!="":
    if not os.path.isfile(args.csv):
        print "Error! Module list file "+args.csv+" not found!"
        exit(1)
    CSVFile = open(args.csv, "r")
    CSVReader = csv.reader(CSVFile)
    for line in CSVReader:
        if line[0]=='': continue
        modulemap[line[3]] = line[0]
        selectedmodules.append(line[3])
        
if args.list!="":
    selectedmodules = []
    if not os.path.isfile(args.list):
        print "Error! Module list file "+args.list+" not found!"
        exit(1)
    ModuleFile = open(args.list, "r")
    for line in ModuleFile: selectedmodules.append(line.strip())

def ModuleName(directory):
    ModuleName = directory[directory.find("M-"):directory.find("_")]
    if ModuleName in modulemap: ModuleName = modulemap[ModuleName]
    return ModuleName

def ProcessTBM(directory):
    os.chdir(inputdir+"/"+directory+"/000_FPIXTest_"+args.temp)
    TBMPhase = int(os.popen("grep basee tbmParameters_C0a.dat | awk '{print $3}'").readline().strip(),16)
    ROCDelayA = int(os.popen("grep basea tbmParameters_C0a.dat | awk '{print $3}'").readline().strip(),16)
    ROCDelayB = int(os.popen("grep basea tbmParameters_C0b.dat | awk '{print $3}'").readline().strip(),16)
    os.chdir(outputdir)
    module = ModuleName(directory)
    if not os.path.isdir(module): os.mkdir(module)
    os.chdir(module)
    TBMFile = open("TBM_module_"+module+".dat", "w")
    print >> TBMFile, """%s
TBMABase0: 0
TBMBBase0: 0
TBMAAutoReset: 0
TBMBAutoReset: 0
TBMANoTokenPass: 0
TBMBNoTokenPass: 0
TBMADisablePKAMCounter: 1
TBMBDisablePKAMCounter: 1
TBMAPKAMCount: 5
TBMBPKAMCount: 5
TBMPLLDelay: %d
TBMADelay: %d
TBMBDelay: %d""" %(module+"_ROC0", TBMPhase, ROCDelayA, ROCDelayB)
    TBMFile.close()
    os.chdir(workingdir)

def ProcessROCs(directory):
    daclist = ["vdig", "vana", "vsh", "vcomp", "vwllpr", "vwllsh", "vhlddel", "vtrim", "vthrcomp", "vibias_bus", "phoffset", "vcomp_adc", "phscale", "vicolor", "vcal", "caldel", "wbc", "ctrlreg", "readback"]
    os.chdir(inputdir+"/"+directory+"/000_FPIXTest_"+args.temp)
    ROCParameters = []
    for iroc in range(16):
        ROCParameters.append([])
        for idac in range(len(daclist)):
            value = os.popen("grep "+daclist[idac]+" dacParameters35_C"+str(iroc)+".dat | awk '{print $3}'").readline().strip()
            if daclist[idac]=="readback": value="12"
            ROCParameters[iroc].append(value)
            if daclist[idac]=="caldel": ROCParameters[iroc].append("61")
    os.chdir(outputdir)
    module = ModuleName(directory)
    os.chdir(module)
    parameterlist = ["Vdd", "Vana", "Vsh", "Vcomp", "VwllPr", "VwllSh", "VHldDel", "Vtrim", "VcThr", "VIbias_bus", "PHOffset", "Vcomp_ADC", "PHScale", "VIColOr", "Vcal", "CalDel", "TempRange", "WBC", "ChipContReg", "Readback"]
    whitespace = "               "
    ROCFile = open("ROC_DAC_module_"+module+".dat", "w")
    for iroc in range(16):
        print >> ROCFile, "ROC:           "+module+"_ROC"+str(iroc)
        for ipar in range(len(parameterlist)):
            print >> ROCFile, parameterlist[ipar]+":"+whitespace[:15-len(parameterlist[ipar])-1]+ROCParameters[iroc][ipar]
    ROCFile.close()
    os.chdir(workingdir)

def ProcessTrims(directory):
    os.chdir(inputdir+"/"+directory+"/000_FPIXTest_"+args.temp)
    TrimParameters = []
    for iroc in range(16):
        TrimBits = [[0]*80 for i in range(52)]
        TrimInputFile = open("trimParameters35_C"+str(iroc)+".dat", "r")
        for line in TrimInputFile:
            TrimList = line.split()
            TrimBit = hex(int(TrimList[0])).split("x")[1]
            PixCol = int(TrimList[2])
            PixRow = int(TrimList[3])
            TrimBits[PixCol][PixRow] = TrimBit
        TrimParameters.append(TrimBits)
        TrimInputFile.close()
    os.chdir(outputdir)
    module = ModuleName(directory)
    os.chdir(module)
    TrimFile = open("ROC_Trims_module_"+module+".dat", "w")
    for iroc in range(16):
        print >> TrimFile, "ROC:     "+module+"_ROC"+str(iroc)
        for icol in range(52):
            if icol < 10: col="0"+str(icol)
            else: col=str(icol)
            print >> TrimFile, "col"+col+":   "+"".join(TrimParameters[iroc][icol])
    TrimFile.close()
    os.chdir(workingdir)

def ProcessMasks(directory):
    os.chdir(outputdir)
    module = ModuleName(directory)
    os.chdir(module)
    MaskFile = open("ROC_Masks_module_"+module+".dat", "w")
    for iroc in range(16):
        print >> MaskFile, "ROC:     "+module+"_ROC"+str(iroc)
        for icol in range(52):
            if icol < 10: col="0"+str(icol)
            else: col=str(icol)
            print >> MaskFile, "col"+col+":   11111111111111111111111111111111111111111111111111111111111111111111111111111111"
    MaskFile.close()
    os.chdir(workingdir)

if args.temp=="p17": temperature = "17C"
if args.temp=="m20": temperature = "m20C"
modulelist = os.popen("/bin/ls "+args.input+" | egrep 'M-[A-Z]-[A-Z0-9]-[A-Z0-9][A-Z0-9]_.*-"+temperature+"'").readlines()
for module in modulelist:
    if selectedmodules==[]: skipmodule = False
    else: skipmodule = True
    module = module.strip()
    for selectedmodule in selectedmodules:
        if module.find(selectedmodule) != -1:
            skipmodule = False
            break
    if skipmodule: continue
    if args.verbose: print "Converting files in "+module+"->"+ModuleName(module)
    ProcessTBM(module)
    ProcessROCs(module)
    ProcessTrims(module)
    ProcessMasks(module)

if args.verbose: print "Done!"
