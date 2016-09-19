#!/usr/bin/env python
import argparse
import os
import re

parser = argparse.ArgumentParser(description="Convert the calibration results in the Production Test Area to POS format for Jordan")
parser.add_argument("-d","--directory", dest="directory", default="../ProductionDebugResults/BatchEROCsm20Results/", help="Input Directory")
parser.add_argument("-v","--verbose", dest="verbose", action="store_true", default=False, help="Enable Verbose Output")
args = parser.parse_args()

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

def SummaryTable():
    Results = []
    for idir in os.listdir(args.directory):
        result = []
        filename = args.directory+idir+"/000_FPIXROCTest_m20/commander_FPIXROCTest.log"
        if args.verbose: print "Processing: "+filename
        ROCPattern = re.compile("E-[0-9][0-9]-[A-Z][A-Z]")
        ROCName = filename[ROCPattern.search(filename).start():ROCPattern.search(filename).end()]
        result.append(ROCName)
        result.append(os.popen("grep 'number of dead pixels' "+filename+" | awk '{print $10}'").readline().strip())
        result.append(os.popen("grep 'number of red-efficiency pixels' "+filename+" | awk '{print $9}'").readline().strip())
        rootfile=ROOT.TFile(args.directory+idir+"/000_FPIXROCTest_m20/commander_FPIXROCTest.root")
        result.append(str(round(rootfile.Get("Scurves/dist_thr_scurveVcal_Vcal_C0_V0").GetMean(),2)))
        #result.append(str(round(rootfile.Get("Scurves/dist_sig_scurveVcal_Vcal_C0_V0").GetMean(),3)))
        result.append(str(round(TH2ToTH1(rootfile.Get("Scurves/sig_scurveVcal_Vcal_C0_V0")).GetMean(),3)))
        result.append(os.popen("grep 'number of dead bumps' "+filename+" | awk '{print $10}'").readline().strip())
        Results.append(result)
    print "\n================================================================================"
    print "Summary Table"
    print "================================================================================"
    print "ROC Name   Dead Pixels   Ineff. Pixels   Vcal Mean   Vcal Width   Dead Bumps"
    for result in Results:
        print '{:<11}'.format(result[0])+'{:<14}'.format(result[1])+'{:<16}'.format(result[2])+'{:<12}'.format(result[3])+'{:<13}'.format(result[4])+result[5]
    print ""

def SummaryPlots():
    print "Making Summary Plots"
    colors = [1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 20, 25, 30, 35, 38, 40, 41, 45, 46]
    histlist = ["Scurves/dist_thr_scurveVcal_Vcal_C0_V0", "Scurves/dist_sig_scurveVcal_Vcal_C0_V0", "BB3/dist_rescaledThr_C0_V0", "Scurves/sig_scurveVcal_Vcal_C0_V0"]
    tfilelist = []
    maximum = [0]*len(histlist)
    for idir in os.listdir(args.directory):
        if args.verbose: print "Loading: "+args.directory+idir+"/000_FPIXROCTest_m20/commander_FPIXROCTest.root"
        tfilelist.append(ROOT.TFile(args.directory+idir+"/000_FPIXROCTest_m20/commander_FPIXROCTest.root"))
        for ihist in range(len(histlist)):
            hist = tfilelist[-1].Get(histlist[ihist])
            if hist.ClassName()[:3]=="TH2": histmax = TH2ToTH1(hist,64,16).GetMaximum()
            else: histmax = hist.GetMaximum()
            if histmax*1.1 > maximum[ihist]: maximum[ihist]=histmax*1.1
    can = ROOT.TCanvas("can","can",800,800)
    for ihist in range(len(histlist)):
        hists=[]
        if histlist[ihist].find("thr_scurveVcal_Vcal")!=-1: can.SetLogy(1)
        else: can.SetLogy(0)
        leg = ROOT.TLegend(0.6,0.5,0.9,0.9);
        leg.SetNColumns(2)
        leg.SetFillColor(0)
        if args.verbose: print "Ploting: "+histlist[ihist]
        for ifile in range(len(tfilelist)):
            tfilelist[ifile].cd()
            hist = tfilelist[ifile].Get(histlist[ihist])
            if hist.ClassName()[:3]=="TH2":
                hists.append(TH2ToTH1(hist,64,16))
                hists[-1].GetXaxis().SetTitle(hist.GetTitle().split("_")[2])
                hist=hists[-1]
            hist.SetLineColor(colors[ifile])
            hist.SetLineWidth(2)
            if ifile==0:
                if histlist[ihist] == "Scurves/dist_thr_scurveVcal_Vcal_C0_V0": hist.GetXaxis().SetRangeUser(0,75)
                if can.GetLogy(): hist.SetMinimum(0.5)
                else: hist.SetMinimum(0)
                hist.SetMaximum(maximum[ihist])
                hist.Draw("hist")
            else: hist.Draw("hist same")
            filename = tfilelist[ifile].GetName()
            ROCPattern = re.compile("E-[0-9][0-9]-[A-Z][A-Z]")
            ROCName = filename[ROCPattern.search(filename).start():ROCPattern.search(filename).end()]
            leg.AddEntry(hist,ROCName,"l")
        leg.Draw()
        can.SaveAs("BatchEROCAnalysis_"+histlist[ihist][histlist[ihist].rfind("/")+1:]+".png")

SummaryTable()
SummaryPlots()

print "Done!"
