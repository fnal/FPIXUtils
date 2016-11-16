#!/usr/bin/env python
import argparse
import math
import os
import re

parser = argparse.ArgumentParser(description="Plotter for BatchE single chip devices")
parser.add_argument("-d","--directories", dest="directories", nargs='+', default=["../ProductionDebugResults/BatchEROCsm20Results","../ProductionDebugResults/BatchEROCsPostIrradiationm20Results"], help="Input Directories")
parser.add_argument("-l","--legend", dest="legend", nargs='+', default=["Pre-Irradiation","Post-Irradiation"], help="Label in Legend")
parser.add_argument("-v","--verbose", dest="verbose", action="store_true", default=False, help="Enable Verbose Output")
args = parser.parse_args()

ROCPattern = re.compile("E-[0-9][0-9]-[A-Z][A-Z]")

import ROOT
ROOT.gStyle.SetOptStat(000000)

def TH2ToTH1(hist, xbins=0, xmax=0):
    if xbins==0: xbins = int(hist.GetMaximum()+1)
    if xmax==0: xmax = int(hist.GetMaximum()+1)
    newhist = ROOT.TH1D(hist.GetName()+"_Projection",hist.GetTitle(),xbins,0,xmax)
    for xbin in range(1,hist.GetNbinsX()+1):
        for ybin in range(1,hist.GetNbinsY()+1):
            newhist.Fill(hist.GetBinContent(xbin,ybin))
    return newhist

def histsearch(histname,tfile,phfilter=""):
    histdir = histname[:histname.rfind("/")]
    histfilter = histname[histname.rfind("/")+1:]
    tdir = tfile.Get(histdir)
    matchdict = {}
    for key in tdir.GetListOfKeys():
        HistPattern = re.compile(histfilter)
        if HistPattern.match(key.GetName()) is not None:
            if histdir+"/"+key.GetName() and phfilter=="":
                return tfile.Get(histdir+"/"+key.GetName())
            elif histdir+"/"+key.GetName() and phfilter!="":
                hist = tfile.Get(histdir+"/"+key.GetName())
                for xbin in range(1,hist.GetNbinsX()+1):
                    if hist.GetBinContent(xbin)>0:
                        matchdict[hist.GetBinContent(xbin)]=histdir+"/"+key.GetName()
                        break
    if phfilter=="max": hist = tfile.Get(matchdict[max(matchdict)])
    if phfilter=="min": hist = tfile.Get(matchdict[min(matchdict)])
    return hist

def MakeIVPlot(directory):
    ROCName = directory[ROCPattern.search(directory).start():ROCPattern.search(directory).end()]
    IVFile = os.popen("find "+directory+" -name ivCurve.log | egrep -v 'Duplicate|Busted'").readline().strip()
    IVData = open(IVFile, 'r')
    IVHist = ROOT.TH1D(ROCName+"IV","IV Curve",61,-5,605)
    for line in IVData:
        if line[0]=="#": continue
        voltage = round(math.fabs(float(line.split()[0])),1)
        current = math.fabs(float(line.split()[1]))
        IVHist.Fill(voltage,current)
    return IVHist

print "Making Summary Plots"
colors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 20, 25, 30, 35, 38, 40, 41, 45, 46]
histlist = ["Scurves/dist_thr_scurveVcal_Vcal_C0_V0", "Scurves/dist_sig_scurveVcal_Vcal_C0_V0", "BB3/dist_rescaledThr_C0_V0", "Scurves/sig_scurveVcal_Vcal_C0_V0","PhOptimization/dist_PH_mapLowVcal_C0_V0","PhOptimization/dist_PH_mapVcal50_C0_V0","PhOptimization/dist_PH_mapHiVcal_C0_V0","PhOptimization/PH_c[0-9][0-9]*_r[0-9][0-9]*_C0_V0","PhOptimization/PH_c[0-9][0-9]*_r[0-9][0-9]*_C0_V0","GainPedestal/gainPedestalNonLinearity_C0_V0","IV"]
tfilelist = []
ivhists = []
ROCListAll = []
ROCList = []
maximum = [0]*len(histlist)
phfilter = "min"

for idir in os.listdir(args.directories[0]):
    ROCName = idir[ROCPattern.search(idir).start():ROCPattern.search(idir).end()]
    ROCListAll.append(ROCName)
for iroc in ROCListAll:
    ROCCount = 0
    for idir in args.directories:
        for jdir in os.listdir(idir):
            if jdir.find(iroc) != -1: ROCCount+=1
    if ROCCount == len(args.directories): ROCList.append(iroc)

for iroc in ROCList:
    shorttfilelist = []
    for idir in args.directories:
        filename = os.popen("find "+idir+" -name '*.root' | grep 000 | egrep -v 'Duplicate|Busted' | grep "+iroc).readline().strip()
        dirname = filename[:filename.find("000")]
        if args.verbose: print "Loading: "+filename
        shorttfilelist.append(ROOT.TFile(filename))
        for ihist in range(len(histlist)):
            if histlist[ihist].find("*") != -1:
                hist=histsearch(histlist[ihist],shorttfilelist[-1],phfilter)
                if phfilter=="min": phfilter="max"
                elif phfilter=="max": phfilter="min"
            elif histlist[ihist]=="IV":
                hist = MakeIVPlot(dirname)
                ivhists.append(hist)
            else: hist = shorttfilelist[-1].Get(histlist[ihist])
            if hist.ClassName()[:3]=="TH2": histmax = TH2ToTH1(hist,64,16).GetMaximum()
            else: histmax = hist.GetMaximum()
            if histmax*1.1 > maximum[ihist]: maximum[ihist]=histmax*1.1
    tfilelist.append(shorttfilelist)
can = ROOT.TCanvas("can","can",800,800)
phfilter="min"
for ihist in range(len(histlist)):
    hists=[]
    if histlist[ihist].find("thr_scurveVcal_Vcal")!=-1 or histlist[ihist].find("IV")!=-1: can.SetLogy(1)
    else: can.SetLogy(0)
    if histlist[ihist].find("PH_c")!=-1 or histlist[ihist]=="IV": leg = ROOT.TLegend(0.6,0.2,0.9,0.3)
    elif histlist[ihist].find("dist_PH_mapHiVcal")!=-1: leg = ROOT.TLegend(0.35,0.8,0.65,0.9)
    else: leg = ROOT.TLegend(0.6,0.8,0.9,0.9)
    leg.SetFillColor(0)
    if args.verbose: print "Ploting: "+histlist[ihist]
    for ifilelist in tfilelist:
        for ifile in range(len(ifilelist)):
            ifilelist[ifile].cd()
            if histlist[ihist].find("*") != -1: hist=histsearch(histlist[ihist],ifilelist[ifile],phfilter)
            elif histlist[ihist]=="IV": hist = ivhists[ifile]
            else: hist = ifilelist[ifile].Get(histlist[ihist])
            if hist.ClassName()[:3]=="TH2":
                hists.append(TH2ToTH1(hist,64,16))
                hists[-1].GetXaxis().SetTitle(hist.GetTitle().split("_")[2])
                hist=hists[-1]
            hist.SetLineColor(colors[ifile])
            hist.SetLineWidth(2)
            if ifile==0:
                if histlist[ihist] == "Scurves/dist_thr_scurveVcal_Vcal_C0_V0": hist.GetXaxis().SetRangeUser(0,75)
                if histlist[ihist] == "Scurves/sig_scurveVcal_Vcal_C0_V0": hist.GetXaxis().SetRangeUser(0,10)
                if histlist[ihist] == "GainPedestal/gainPedestalNonLinearity_C0_V0": hist.GetXaxis().SetRangeUser(0.85,1.05)
                if histlist[ihist]=="IV": hist.SetMinimum(5.0e-12)
                elif can.GetLogy(): hist.SetMinimum(0.5)
                else: hist.SetMinimum(0)
                hist.SetMaximum(maximum[ihist])
                hist.Draw("hist")
            else: hist.Draw("hist same")
            filename = ifilelist[ifile].GetName()
            ROCName = filename[ROCPattern.search(filename).start():ROCPattern.search(filename).end()]
            if len(args.legend)>=ifile: leg.AddEntry(hist,ROCName+" "+args.legend[ifile],"l")
        leg.Draw()
        outputname = histlist[ihist][histlist[ihist].rfind("/")+1:]
        if outputname.find("*")!=-1:
            if phfilter=="min":
                phfilter="max"
                outputname = "PH_MinPixel_C0_V0"
            elif phfilter=="max":
                phfilter="min"
                outputname = "PH_MaxPixel_C0_V0"
        filename = ifilelist[0].GetName()
        ROCName = filename[ROCPattern.search(filename).start():ROCPattern.search(filename).end()]
        can.SaveAs("BatchEPrePost_"+ROCName+"_"+outputname+".png")
        leg.Clear()

print "Done!"
