#add info here:

#import libraries here
# _     _________________  ___  ______ _____ _____ _____ 
#| |   |_   _| ___ \ ___ \/ _ \ | ___ \_   _|  ___/  ___|
#| |     | | | |_/ / |_/ / /_\ \| |_/ / | | | |__ \ `--. 
#| |     | | | ___ \    /|  _  ||    /  | | |  __| `--. \
#| |_____| |_| |_/ / |\ \| | | || |\ \ _| |_| |___/\__/ /
#\_____/\___/\____/\_| \_\_| |_/\_| \_|\___/\____/\____/                                                                                                                                
                                                               
from optparse import OptionParser
parser = OptionParser()
import sys
import glob
import re
import os
import numpy as np
from array import * 
from ROOT import *

#Here list the parser options 
# _ __   __ _ _ __ ___  ___ _ __ 
#| '_ \ / _` | '__/ __|/ _ \ '__|
#| |_) | (_| | |  \__ \  __/ |   
#| .__/ \__,_|_|  |___/\___|_|   
#| |                             
#|_| 
#

myfilename = ".root" #"_pa225_090915.root"
myfileoutname = "XRFResult_"

parser.add_option('--setup', type='string', action='store',
                  default='UIC',
                  dest='setup',
                  help='Setup corresponding to KU or UIC?: Options KU or UIC only')

parser.add_option('--outputfile', type='string', action='store',
                  default='M_',
                  dest='outputfile',
                  help='Set first part of the name of outputfile: Usually M_XX_YYY')

parser.add_option('--histoname', type='string', action='store',
                  default='Xray/q',
                  dest='histoname',
                  help='Histogram that is analyzed')

parser.add_option('--sigma', type='int', action='store',
                  default=6,
                  dest='sigma',
                  help='Value of sigma to be used to find peaks in TSpectrum')

parser.add_option('--threshold', type='float', action='store',
                  default=0.5,
                  dest='threshold',
                  help='Value of the threshold to be used to find peaks in TSpectrum')

parser.add_option('--XRSource', type='string', action='store',
                  default='Cu',
                  dest='XRSource',
                  help='Name of the XRay source, valid options: Cu or Mo ')

parser.add_option('--CuFile', type='string', action='store',
                  default='Fluorescence.root',
                  dest='CuFile',
                  help='Name of the Cu root file (when Mo is the XRaySource) ')

parser.add_option('--MoFile', type='string', action='store',
                  default='Fluorescence.root',
                  dest='MoFile',
                  help='Name of the Mo root file (when Cu is the XRaySource ')

parser.add_option('--AgFile', type='string', action='store',
                  default='Fluorescence.root',
                  dest='AgFile',
                  help='Name of the Ag root file ')

parser.add_option('--SnFile', type='string', action='store',
                  default='Fluorescence.root',
                  dest='SnFile',
                  help='Name of the Sn root file ')
parser.add_option('--InFile', type='string', action='store',
                  default='Fluorescence.root',
                  dest='InFile',
                  help='Name of the In root file ')

parser.add_option('--nrocs', type='int', action='store',
                  default=16,
                  dest='nrocs',
                  help='Number or rocs')
parser.add_option('--badrocs', type='string', action='store',
                  default='17',
                  dest='badrocs',
                  help='List of bad rocs, for example [2,4,5]')
(options, args) = parser.parse_args()
argv = []
#define functions here:
#  _   _   _   _   _   _   _   _   _  
# / \ / \ / \ / \ / \ / \ / \ / \ / \ 
#( f | u | n | c | t | i | o | n | s )
# \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ 

#Comments on get_gpeaks: To get rid of the polymarkers of the Spectrum method, use the option ='goff' in the search function
def get_gpeaks(h,lrange=[20,300],sigma=6,opt="goff",thres=0.05,niter=1000):
    s = TSpectrum(niter,1)
    h.GetXaxis().SetRange(lrange[0],lrange[1])
    s.Search(h,sigma,opt,thres)
    s.SetAverageWindow(2)
    bufX, bufY = s.GetPositionX(), s.GetPositionY()
    pos = []
    for i in range(s.GetNPeaks()):
        pos.append([bufX[i], bufY[i]])
    pos.sort()
    return pos
#Comments on rm_peak: Gets rid of the additional peak that KU observes
def rm_peak(histo, gaus):
    bins = histo.GetNbinsX()
    print 'P0',gaus.GetParameter(0),gaus.GetParameter(1),gaus.GetParameter(2)
    newhisto = histo.Clone()	
    newhisto.Reset()
    for i in range( 1 , bins) :
        #val = histo.GetBinContent(i) - gaus.Eval(i)
        val = gaus.Eval(i*2)
        newhisto.Fill(i*2,val) 
    histo.Add(newhisto,-1)
    return histo

#Comments on FitPeaks: It has 2 variants  depending on the Xray source used. It will get the peaks and fit them and save the stats info in .txt files per Material and ROC.
def FitPeaks(rootfile,histo,material,rocs,output,XRSource,rebin):
    arrayMo = false
    arrayCu = false
    arrayIn = false 
    arrayAg = false
    arraySn = false
    grocs = len(rocs)+1
    ArrayG = TObjArray(16)
    if material == 'Mo':
        arrayMo = true
        ArrayMo = TObjArray(16)
    elif material == 'Ag':
        arrayAg = true
        ArrayAg = TObjArray(16)
    elif material == 'Sn':
        arraySn =true
        ArraySn = TObjArray(16)
    elif material == 'In':
        arrayIn = true
        ArrayIn = TObjArray(16)
    elif material == 'Cu':
        arrayCu = true
        ArrayCu = TObjArray(16)
    #for i in range(0,int(nrocs)-1):
    for i in range(0,16):
        if i not in rocs:
            print 'Skipping roc', i
            stats= open(output+material+'C_'+str(i)+'_stats.txt','w')
            stats.writelines(["Mean_Mo_C"+str(i)+":\t"+"0.0"+"\n", "Sigma_Mo_C"+str(i)+":\t"+"0.0"+"\n","Mean_"+material+"_C"+str(i)+":\t"+"0.0"+"\n", "Sigma_"+material+"_C"+str(i)+":\t"+"0.0"+"\n"])
            continue  
        stats= open(output+material+'C_'+str(i)+'_stats.txt','w')
        hist = histo +str(i)+"_V0"
        directory = rootfile.Get('Xray')
        keys = directory.GetListOfKeys()
        allkeys = []
        for key in keys:
            allkeys.append(key.GetName())
        print hist, hist.strip('Xray/')
        if hist.strip('Xray/') in allkeys:
            print 'FoilandRoc found:', hist
         #if  hist not in key.GetName():
                #print 'Target foil not found'
                #continue
        else:
            print 'Histogram needed not  found'
            continue   
        tgt = rootfile.Get(hist)
        print "Opening file:"+ hist
        tgt.Rebin(rebin)
        tgt.Draw()
        tgt.GetXaxis().SetRange(20,300)
        peaks = get_gpeaks(tgt)
        print len(peaks), "Roc: ", i, material
        if len(peaks)==0:
            print 'Couldnt find peaks, check here!'
            continue
        mid1 = peaks[0][1]
        mid2 = peaks[1][1]
        rebinned = false 
        if(len(peaks)>3):
            print "Too many peaks,rebinning"
            tgt.Rebin(2)
            peaks = get_gpeaks(tgt)
            if (len(peaks)==2):
                mid1 = peaks[0][1]
                mid2 = peaks[1][1]
                rebinned = true 
            #peaks = peaks[1:3] 
        if (len(peaks)==2 or rebinned):
            for t in range(1, int(peaks[0][0])):
                if (tgt.GetBinContent(t)/mid1>0.68):
                    sigma1l = t 
                    break
            for j in range(int(peaks[0][0])+1,int(peaks[1][0])):
                if (tgt.GetBinContent(j)/mid1<0.68):
                    sigma1r = j
                    break
            for l in range(int(peaks[1][0])+1,300):
                if (tgt.GetBinContent(l)/mid2<0.68):
                    sigma2r = l
                    break
            for k in range(int(peaks[0][0])+(sigma1r)/2,int(peaks [1][0])):
                if (tgt.GetBinContent(k)/mid2>0.68) and abs(k-peaks[1][0])<20:
                    sigma2l = k
                    break
        if(len(peaks)==3):
            if peaks[1][1] > peaks[2][1]:
                mid3 = peaks[1][1]
                right3 = int(peaks[1][0])
                for t in range(1, int(peaks[0][0])):
                    if (tgt.GetBinContent(t)/mid1>0.68):
                        sigma1l = t 
                        break
                for j in range(int(peaks[0][0])+1,right3):
                    if (tgt.GetBinContent(j)/mid1<0.68):
                        sigma1r = j
                        break
                for l in range(right3+1,300):
                    if (tgt.GetBinContent(l)/mid3<0.68):
                        sigma2r = l
                        break
                for k in range(int(peaks[0][0])+(sigma1r)/2,right3):
                    if (tgt.GetBinContent(k)/mid3>0.68):
                        sigma2l = k
                        if abs(k-right3)< 20:
                            break
            else:
                mid3 = peaks[2][1] 
                right3 = int(peaks[2][0])
                for t in range(1, int(peaks[0][0])):
                    if (tgt.GetBinContent(t)/mid1>0.68):
                        sigma1l = t 
                        break
                for j in range(int(peaks[0][0])+1,int(peaks[1][0])):
                    if (tgt.GetBinContent(j)/mid1<0.68):
                        sigma1r = j
                        break
                for l in range(right3+1,300):
                    if (tgt.GetBinContent(l)/mid3<0.68):
                        sigma2r = l
                        break
                for k in range(int(peaks[1][0])+(sigma1r)/2,right3):
                    if (tgt.GetBinContent(k)/mid3>0.68) and abs(k-right3)<20:
                        sigma2l = k
                        break
        if (XRSource  == 'Mo'):
            if (material == 'Cu'):
                gaus1 = TF1("gaus1","gaus",peaks[1][0]-15, peaks[1][0]+15)
                gaus2 = TF1("gaus2","gaus",peaks[0][0]-15, peaks[0][0]+15)
            elif (material == 'Sn' or material == 'Ag' or material == 'In' and len(peaks) == 3):
                gaus1 = TF1("gaus1","gaus",peaks[1][0]-15, peaks[1][0]+15)
                gaus2 = TF1("gaus2","gaus",peaks[2][0]-20, peaks[2][0]+20)
            elif (material == 'Sn' or material == 'Ag' or material == 'In' and len(peaks) == 2):
	        gaus1 = TF1("gaus1","gaus",peaks[0][0]-15, peaks[0][0]+15)
                gaus2 = TF1("gaus2","gaus",peaks[1][0]-15, peaks[1][0]+15)
            tgt.Fit("gaus1","R")
            tgt.Fit("gaus2","+R")
            tgt.Draw()
	    print tgt.GetFunction("gaus2").GetParameter(1)
            newhisto = rm_peak(tgt,tgt.GetFunction("gaus1"))
	    print "Got new histo"
            c1.Update()
	    newhisto.Fit("gaus2","+R")
            mu1 = tgt.GetFunction("gaus1").GetParameter(1)
            mu2 = newhisto.GetFunction("gaus2").GetParameter(1)
            sigma1 = tgt.GetFunction("gaus1").GetParameter(2)
            sigma2 = newhisto.GetFunction("gaus2").GetParameter(2)
            print mu1 , sigma1, mu2, sigma2
            c1.SaveAs(output+'FitC_'+str(i)+material+'.png')
            stats.writelines(["Mean_Mo_C"+str(i)+":\t"+str(mu1)+"\n", "Sigma_Mo_C"+str(i)+":\t"+str(sigma1)+"\n","Mean_"+material+"_C"+str(i)+":\t"+str(mu2)+"\n", "Sigma_"+material+"_C"+str(i)+":\t"+str(sigma2)+"\n"])
            newhisto.Draw()
	    c1.Update()
	    c1.SaveAs(output+'Stripped_C'+str(i)+'_'+material+'.png')
            if arrayCu:
                ArrayCu.AddAt(tgt,i)
            elif arrayAg:
                ArrayAg.AddAt(tgt,i)
            elif arraySn:
                ArraySn.AddAt(tgt,i)
            elif arrayIn:
                ArrayIn.AddAt(tgt,i)
        elif (XRSource == 'Cu'):
            gaus1 = TF1("gaus1","gaus",peaks[0][0]-15, peaks[0][0]+15)
            if len(peaks)==2: gaus2 = TF1("gaus2","gaus",peaks[1][0]-15,peaks[1][0]+15)
            if len(peaks)==3:
                if peaks[1][1]>peaks[2][1]:
                    gaus2 = TF1("gaus2","gaus",peaks[1][0]-20,peaks[1][0]+20)
                else:
                    gaus2 = TF1("gaus2","gaus",peaks[2][0]-20,peaks[2][0]+20)
            tgt.Fit("gaus1","R")
            tgt.Fit("gaus2","+R")
            tgt.Draw()
            c1.Update()
            mu1 = tgt.GetFunction("gaus1").GetParameter(1)
            mu2 = tgt.GetFunction("gaus2").GetParameter(1)
            sigma1 = tgt.GetFunction("gaus1").GetParameter(2)
            sigma2 = tgt.GetFunction("gaus2").GetParameter(2)
            print mu1 , sigma1, mu2, sigma2
            c1.SaveAs(output+'FitC_'+str(i)+material+'.png')
            stats.writelines(["Mean_Cu_C"+str(i)+":\t"+str(mu1)+"\n", "Sigma_Cu_C"+str(i)+":\t"+str(sigma1)+"\n","Mean_"+material+"_C"+str(i)+":\t"+str(mu2)+"\n", "Sigma_"+material+"_C"+str(i)+":\t"+str(sigma2)+"\n"])
            if arrayMo:
                ArrayMo.AddAt(tgt,i)
            elif arrayAg:
                ArrayAg.AddAt(tgt,i)
            elif arraySn:
                ArraySn.AddAt(tgt,i)
            elif arrayIn:
                ArrayIn.AddAt(tgt,i)
    if arrayCu:
        ArrayG = ArrayCu
    elif arrayAg:
        ArrayG = ArrayAg
    elif arraySn:
        ArrayG = ArraySn
    elif arrayMo:
        ArrayG = ArrayMo
    elif arrayIn:
        ArrayG = ArrayIn
    return ArrayG
   
#Comments on  : 
def PlotSameNStats(arrayfithisto1, arrayfithisto2, arrayfithisto3, arrayfithisto4, rocs, output, XRSource):
    grocs = len(rocs)   
    for i in rocs:
        if i not in rocs:
            print 'Skipping roc', i
            continue  
        c1 = TCanvas('c1',"Fluorescence test",1)
        gStyle.SetOptStat(0)
        c1.cd()     
        gStyle.SetOptTitle(0)
        height=[]
        if not arrayfithisto1: 
            height.append(0)
            continue 
        else: 
            fithisto1 = arrayfithisto1[i]
            fithisto1.GetXaxis().SetRange(20,300)
            fithisto1.SetLineColor(kBlue)
            mu1f = fithisto1.GetFunction("gaus2").GetParameter(1)
            sigma1f = fithisto1.GetFunction("gaus2").GetParameter(2)
            mu1 = float("{0:.2f}".format(mu1f))
            sigma1 = float("{0:.2f}".format(sigma1f))
            height.append( fithisto1.GetMaximum())
        if not arrayfithisto2:
            height.append(0)
            continue
        else: 
            fithisto2 = arrayfithisto2[i]
            fithisto2.GetXaxis().SetRange(20,300)
            fithisto2.SetLineColor(kMagenta)
            mu2f = fithisto2.GetFunction("gaus2").GetParameter(1)
            sigma2f = fithisto2.GetFunction("gaus2").GetParameter(2)
            mu2 = float("{0:.2f}".format(mu2f))
            sigma2 = float("{0:.2f}".format(sigma2f))
            height.append(fithisto2.GetMaximum())
        if not arrayfithisto3:
            continue
            height.append(0)
        else:
            fithisto3 = arrayfithisto3[i]
            fithisto3.GetXaxis().SetRange(20,300)
            fithisto3.SetLineColor(kGreen)
            mu3f = fithisto3.GetFunction("gaus2").GetParameter(1)
            sigma3f = fithisto3.GetFunction("gaus2").GetParameter(2)
            mu3 = float("{0:.2f}".format(mu3f))
            sigma3 = float("{0:.2f}".format(sigma3f))
            height.append(fithisto3.GetMaximum())
        if not arrayfithisto4:
            continue 
            height.append(0) 
        else:
            fithisto4 = arrayfithisto4[i]
            fithisto4.GetXaxis().SetRange(20,300)
            fithisto4.SetLineColor(kOrange)    
            mu4f = fithisto4.GetFunction("gaus2").GetParameter(1)
            sigma4f = fithisto4.GetFunction("gaus2").GetParameter(2)
            mu4 = float("{0:.2f}".format(mu4f))
            sigma4 = float("{0:.2f}".format(sigma4f))
            height.append( fithisto4.GetMaximum())
        print height        
        maxheight = max(height)
        print maxheight
        if XRSource == 'Mo':
            fithisto1.SetMaximum(maxheight+100)
            fithisto1.Draw()
            c1.Update()
            textmu1 = TLatex()
            textmu1.SetNDC()
            textmu1.SetTextColor(kBlue)
            textmu1.SetTextSize(0.03)
            textmu1.DrawText(0.7,0.25,"Cu.Mean():"+ str(mu1))
            textsigma1 = TLatex()
            textsigma1.SetNDC()
            textsigma1.SetTextColor(kBlue)
            textsigma1.SetTextSize(0.03)
            textsigma1.DrawText(0.7,0.15,"Cu.Sigma():"+ str(sigma1))
            c1.Update()
        elif XRSource == 'Cu':
            fithisto1.SetMaximum(maxheight+100)
            fithisto1.Draw()
            c1.Update()
            textmu1 = TLatex()
            textmu1.SetNDC()
            textmu1.SetTextColor(kBlue)
            textmu1.SetTextSize(0.03)
            textmu1.DrawText(0.7,0.25,"Mo.Mean():"+ str(mu1))
            textsigma1 = TLatex()
            textsigma1.SetNDC()
            textsigma1.SetTextColor(kBlue)
            textsigma1.SetTextSize(0.03)
            textsigma1.DrawText(0.7,0.15,"Mo.Sigma():"+ str(sigma1))
            c1.Update()
        if not arrayfithisto2:
            continue
        else: 
            fithisto2.SetMaximum(maxheight+100)
            fithisto2.Draw("sames")
            textmu2 = TLatex()
            textmu2.SetNDC()
            textmu2.SetTextColor(kMagenta)
            textmu2.SetTextSize(0.03)
            textmu2.DrawText(0.7,0.45,"Ag.Mean():"+ str(mu2))
            textsigma2 = TLatex()
            textsigma2.SetNDC()
            textsigma2.SetTextColor(kMagenta)
            textsigma2.SetTextSize(0.03)
            textsigma2.DrawText(0.7,0.35,"Ag.Sigma():"+ str(sigma2))
            c1.Update()
        if not arrayfithisto3:
            continue
        else: 
            fithisto3.SetMaximum(maxheight+100)
            fithisto3.Draw("sames")
            textmu3 = TLatex()
            textmu3.SetNDC()
            textmu3.SetTextColor(kGreen)
            textmu3.SetTextSize(0.03)
            textmu3.DrawText(0.7,0.65,"Sn.Mean():"+ str(mu3))
            textsigma3 = TLatex()
            textsigma3.SetNDC()
            textsigma3.SetTextColor(kGreen)
            textsigma3.SetTextSize(0.03)
            textsigma3.DrawText(0.7,0.55,"Sn.Sigma():"+ str(sigma3))
            c1.Update()
        if not arrayfithisto4:
            continue
        else: 
            fithisto4.SetMaximum(maxheight+100)
            fithisto4.Draw("sames")
            textmu4 = TLatex()
            textmu4.SetNDC()
            textmu4.SetTextColor(kOrange)
            textmu4.SetTextSize(0.03)
            textmu4.DrawText(0.7,0.85,"In.Mean():"+ str(mu4))
            textsigma4 = TLatex()
            textsigma4.SetNDC()
            textsigma4.SetTextColor(kOrange)
            textsigma4.SetTextSize(0.03)
            textsigma4.DrawText(0.7,0.75,"In.Sigma():"+ str(sigma4))
            c1.Update()
        text = TLatex()
        text.SetNDC()
        text.DrawText(0.4,0.95,"Fluorescence tests C_"+str(i))
        print 'Saving to:', output
        c1.SaveAs(output+"XRayFluoResultsC_"+str(i)+'.png')
        c1.Close()
    return 

def ConversionPlot(rocs,badrocs,output, XRSource):
    grocs = len(rocs)   
    convfactcu = 8048/3.6
    convfactmo = 17479/3.6
    convfactag = 22163/3.6
    convfactsn= 25271/3.6
    convfactin = 24207/3.6
    sumoutfile = "SummaryQPlots_" + output + ".txt"
    sumout = open(sumoutfile, "w")
    sumout.write(myfileoutname + "Summary of QPlots Slopes.\n"+ " e^{-}/Vcal: Intercept: \n" )
    qplotfit = open("SummaryQplots.txt",'w')
    n_oh = TH1F('n_oh','N_o', 100,0,1000)
    slopeh = TH1F('Slope','Slope',100, 0,100)
    qmatrix = np.zeros((16,5))
    for i in xrange(0,16):
        if i in badrocs:
            sumout.write( "C_" + str(i) + " "+ "0.0" + " +/- " + "0.0" +" " + "0.0 "+ " +/- " + "0.0"+ '\n' )
        else: 
#need to space this 
            mu_cu =[]
            sig_cu=[]
            mu_mo = []
            sig_mo = []
            mu_ag =[]
            sig_ag =[]
            mu_sn =[]
            sig_sn = []
            mu_in =[]
            sig_in = []
            for file in glob.glob("*_"+str(i)+"_stats.txt"):
                name = os.path.splitext(file)[0]
                print "Opening:",name
                if XRSource =='Mo':
                    if('CuC_' in name):
                        material = 'Cu'
                        f = open(file,'r')
                        line = f.readlines()
                        for k in range(0,len(line)):
                            if "_Mo" in line[k]:
                                if "Mean_Mo" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meanmo = words[1].strip('\n')
                                    mu_mo.append(meanmo)
                                elif "Sigma_Mo" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigmamo = words[1].strip('\n') 
                                    sig_mo.append(sigmamo)   
                            else:
                                if "Mean_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    mean = words[1].strip('\n')
                                    mu_cu.append(mean)
                                elif "Sigma_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigma = words[1].strip('\n')
                                    sig_cu.append(sigma)
                        f.close()               
                    elif('AgC_' in name):
                        material = 'Ag'
                        f = open(file,'r')
                        line = f.readlines()
                        for k in range(0,len(line)):
                            if "_Mo" in line[k]:
                                if "Mean_Mo" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meanmo = words[1].strip('\n')
                                    mu_mo.append(meanmo)
                                elif "Sigma_Mo" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigmamo = words[1].strip('\n') 
                                    sig_mo.append(sigmamo)   
                            else:
                                if "Mean_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meanag = words[1].strip('\n')
                                    mu_ag.append(meanag)
                                elif "Sigma_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigma = words[1].strip('\n')
                                    sig_ag.append(sigma)
                        f.close()
                    elif('SnC_' in name):
                        material = 'Sn'
                        convfact= 25271/3.6
                        f = open(file,'r')
                        line = f.readlines()
                        for k in range(0,len(line)):
                            if "_Mo" in line[k]:
                                if "Mean_Mo" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meanmo = words[1].strip('\n')
                                    mu_mo.append(meanmo)
                                elif "Sigma_Mo" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigmamo = words[1].strip('\n') 
                                    sig_mo.append(sigmamo)   
                            else:
                                if "Mean_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    mean = words[1].strip('\n')
                                    mu_sn.append(mean)
                                elif "Sigma_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigma = words[1].strip('\n')
                                    sig_sn.append(sigma)
                        f.close()
                    elif('InC_' in name):
                        material = 'In'
                        convfact= 24207/3.6
                        f = open(file,'r')
                        line = f.readlines()
                        for k in range(0,len(line)):
                            if "_Mo" in line[k]:
                                if "Mean_Mo" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meanmo = words[1].strip('\n')
                                    mu_mo.append(meanmo)
                                elif "Sigma_Mo" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigmamo = words[1].strip('\n') 
                                    sig_mo.append(sigmamo)   
                            else:
                                if "Mean_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    mean = words[1].strip('\n')
                                    mu_in.append(mean)
                                elif "Sigma_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigma = words[1].strip('\n')
                                    sig_in.append(sigma)
                        f.close()
                elif XRSource == 'Cu':
                    if('MoC_' in name):
                        material = 'Mo'
                        f = open(file,'r')
                        line = f.readlines()
                        for k in range(0,len(line)):
                            if "_Cu" in line[k]:
                                if "Mean_Cu" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meancu = words[1].strip('\n')
                                    mu_cu.append(meancu)
                                elif "Sigma_Cu" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigmacu = words[1].strip('\n') 
                                    sig_cu.append(sigmacu)   
                            else:
                                if "Mean_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    mean = words[1].strip('\n')
                                    mu_mo.append(mean)
                                elif "Sigma_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigma = words[1].strip('\n')
                                    sig_mo.append(sigma)
                            f.close()               
                    elif('AgC_' in name):
                        material = 'Ag'
                        f = open(file,'r')
                        line = f.readlines()
                        for k in range(0,len(line)):
                            if "_Cu" in line[k]:
                                if "Mean_Cu" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meancu = words[1].strip('\n')
                                    mu_cu.append(meancu)
                                elif "Sigma_Cu" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigmacu = words[1].strip('\n') 
                                    sig_cu.append(sigmacu)   
                            else:
                                if "Mean_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    mean = words[1].strip('\n')
                                    mu_ag.append(mean)
                                elif "Sigma_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigma = words[1].strip('\n')
                                    sig_ag.append(sigma)
                        f.close()
                    elif('SnC_' in name):
                        material = 'Sn'
                        convfact= 25271/3.6
                        f = open(file,'r')
                        line = f.readlines()
                        for k in range(0,len(line)):
                            if "_Cu" in line[k]:
                                if "Mean_Cu" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meancu = words[1].strip('\n')
                                    mu_cu.append(meancu)
                                elif "Sigma_Cu" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigmacu = words[1].strip('\n') 
                                    sig_cu.append(sigmacu)   
                            else:
                                if "Mean_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    mean = words[1].strip('\n')
                                    mu_sn.append(mean)
                                elif "Sigma_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigma = words[1].strip('\n')
                                    sig_sn.append(sigma)
                        f.close()
                    elif('InC_' in name):
                        material = 'In'
                        convfact= 24207/3.6
                        f = open(file,'r')
                        line = f.readlines()
                        for k in range(0,len(line)):
                            if "_Cu" in line[k]:
                                if "Mean_Cu" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    meancu = words[1].strip('\n')
                                    mu_cu.append(meancu)
                                elif "Sigma_Cu" in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigmacu = words[1].strip('\n') 
                                    sig_cu.append(sigmacu)   
                            else:
                                if "Mean_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    mean = words[1].strip('\n')
                                    mu_in.append(mean)
                                elif "Sigma_"+material in line[k]:
                                    words =  re.split(':\t',line[k])
                                    sigma = words[1].strip('\n')
                                    sig_in.append(sigma)
                        f.close()
            n_cu = len(mu_cu)
            n_mo = len(mu_mo)
            n_ag = len(mu_ag)
            n_sn = len(mu_sn)
            n_in = len(mu_in)
            n_all = n_cu + n_mo + n_sn + n_ag+ n_in
            sigma_y = [0]*n_all
            mus = mu_cu + mu_mo + mu_ag + mu_sn + mu_in
            sigma_x = sig_cu + sig_mo + sig_ag+ sig_sn + sig_in
            k_cu = [convfactcu]*n_cu
            k_mo = [convfactmo]*n_mo
            k_ag = [convfactag]*n_ag
            k_sn = [convfactsn]*n_sn
            k_in = [convfactin]*n_in
            k = k_cu + k_mo + k_ag + k_sn+k_in
            matrix = np.zeros(((len(mus)),4))
            print "mus", mus, len(matrix)
            for j in range(0,len(mus)):
                matrix[j][1] = float(mus[j])
                matrix[j][0] = float(k[j])
                matrix[j][3] = float(sigma_x[j])
            table = open('SummaryTable'+'_'+output+'_'+'C_'+str(i)+'.txt','w')
            np.savetxt("SummaryTable"+'_'+output+'_'+"C_"+str(i)+".txt",matrix, delimiter="\t", fmt="%s", newline='\n' )
            gStyle.SetOptFit(1)
            c1 = TCanvas('c1',"Fluorescence test",1)
            c1.cd()
            c1.Update()
            gStyle.SetOptStat(0)
            gr = TGraphErrors("SummaryTable"+'_'+output+'_'+"C_"+str(i)+".txt")
            gr.SetMarkerStyle(41)
            fit = TF1("fit","pol1",1000,10000)
            gr.Fit("fit","w","l",1000,10000)
            gr.SetMarkerStyle(20) 
            title = "Graph eV vs Vcal for ROC " + str(i) + " "
            gr.SetTitle( title )
            n_o = gr.GetFunction("fit").GetParameter(0)
            #n_o_er = gr.GetFunction("fit").GetParameter(1)
            n_o_er = gr.GetFunction("fit").GetParError(0)
            print "no:",n_o
            slope = gr.GetFunction("fit").GetParameter(1)
            slope_err = gr.GetFunction("fit").GetParError(1) 
            print "slope:",slope
            pn_o = -(n_o/slope)
            pn_o_er =abs(n_o_er/slope)
            pslope = 1/slope
            slope_err = gr.GetFunction("fit").GetParError(1)
            pslope_err = slope_err /( slope*slope)
            chisquare = gr.GetFunction("fit").GetChisquare()
            ndf = gr.GetFunction("fit").GetNDF()
            print "no:",pn_o
            print "no error:", pn_o_er
            print "slope:",pslope
            print "slope error:",pslope_err
            sumout.write( "C_" + str(i) + " "+ '{0:.2}'.format(pslope) + " +/- " + '{0:.1}'.format(pslope_err) +" " + '{0:.2}'.format(pn_o) + " +/- " + '{0:.2}'.format(pn_o_er)+ '\n' )
            gStyle.SetOptFit(0)
            gr.Draw("AP")
            gr.GetYaxis().SetRange(0,300)
            gr.GetXaxis().SetRange(0,8000)
            gr.GetYaxis().SetTitle("Vcal")
            gr.GetXaxis().SetTitle("No.Electrons")
            gStyle.SetOptStat(0)
            c1.Update()
            gStyle.SetOptFit(0)
            gr.Draw("AP")
            gStyle.SetOptFit(0)
            #ps = c1.FindObject("Graph").FindObject("stats")
            #ps.SetX1NDC(0.15)
            #ps.SetX2NDC(0.55)
            #gStyle.SetOptStat(0)
            c1.SetGrid()
            textslope = TLatex()
            textslope.SetNDC()
            textslope.SetTextColor(kBlack)
            textslope.SetTextSize(0.05)
            textslope.DrawLatex(0.15,0.9,title)
            textslope.DrawLatex(0.15,0.8,"e^{-}/Vcal: "+ '{0:.2}'.format(pslope) + " \pm " + '{0:.1}'.format(pslope_err) +" Intercept: " + '{0:.2}'.format(pn_o) + " \pm " + '{0:.2}'.format(pn_o_er))
            #textslope.DrawLatex(0.2,0.8,"e^{-}/Vcal:"+ '{:.4}'.format(1./slope) + " +/- " + '{:.4}'.format((slope_err)/pow(slope,2)))
            textslope.DrawLatex(0.15,0.7,"#chi^{2}/ndf = " + '{:.4}'.format(chisquare/ndf))
            textslope.DrawLatex(0.2,0.2,"  Cu                            Mo               Ag   In   Sn")
            #textslope.DrawLatex(0.1,0.91,"ROC "+str(i))
            gStyle.SetOptFit(0)
            c1.Update()
            gStyle.SetOptFit(0)
            c1.Update()
            c1.SaveAs('Qplot'+'_'+output+'_C'+str(i)+'.png')
            c1.Close()
            c1.Update()
            gStyle.SetOptStat(1)
            c1.Update()
            ##get q value of fit and error and add them to a table then use TGraphError to make a distribution of them 
            n_oh.Fill(-n_o/slope)
            slopeh.Fill(1/slope)
            qmatrix[i][0] = 1/slope
            qmatrix[i][1] = -n_o/slope
            qmatrix[i][2] = chisquare
            qmatrix[i][3] = ndf
            qmatrix[i][4] = slope_err/pow(slope,2)
    	# Create SummaryQPlots txt file:
    np.savetxt("SummaryDistributionTable"+'_'+output+'_'+".txt",qmatrix, delimiter="\t", fmt="%s", newline='\n' )
    FormattedFile = open("FluorescenceFormattedOutput.txt", "w")
    FormattedFile.write("Roc Number    Slope (e-/Vcal)     Offset (Vcal)    Chi2/NDf\n")
    for iroc in rocs:
        FormattedFile.write("ROC "+str(iroc)+"         "+str(round(qmatrix[iroc][0],2))+" +/- "+str(round(qmatrix[iroc][4],4))+"       "+str(int(round(qmatrix[iroc][1])))+"             "+str(round(qmatrix[iroc][2]/qmatrix[iroc][3],4))+"\n")
    FormattedFile.close()
    c2 = TCanvas('c2',"Distribution N_o",1)
    c2.cd()
    gStyle.SetOptStat(1)
    n_oh.Draw()
    n_oh.SetStats(1)
    c2.Update()
    ps2 = n_oh.GetListOfFunctions().FindObject("stats")
    gStyle.SetOptStat(0)
    n_oh.Draw()
    c2.Update()
    c2.SaveAs(output+'Distribution_NoEle.png')
    c3 = TCanvas('c3',"Distribution N_o",1)
    c3.cd()
    gStyle.SetOptStat(1)
    slopeh.Draw()
    slopeh.SetStats(1)
    c3.Update()
    slopeh.GetXaxis().SetTitle("p1[Vcal/No.Ele]")
    slopeh.GetYaxis().SetTitle("Entries")
    gStyle.SetOptStat(1)
    slopeh.Draw()
    c3.Update()
    c3.SaveAs(output+'Distribution_Slope.png')
    sumout.close()
    return  

#                 _       
# _ __ ___   __ _(_)_ __  
#| '_ ` _ \ / _` | | '_ \ 
#| | | | | | (_| | | | | |
#|_| |_| |_|\__,_|_|_| |_|

if options.setup == 'UIC':                         
    rootfile1 = TFile(options.MoFile)
    rootfile1name = options.MoFile
    material1 = 'Mo'
    XRSource  = 'Cu'
elif options.setuo =='KU':
    rootfile1 = TFile(options.CuFile)
    rootfile1name = options.CuFile
    material1 = 'Cu'
    XRSource  = 'Mo'
rootfile2 = TFile(options.AgFile)
rootfile2name = options.AgFile
rootfile3 = TFile(options.SnFile)
rootfile3name = options.SnFile
rootfile4 = TFile(options.InFile)
rootfile4name = options.InFile
histname = options.histoname
nrocs = options.nrocs
Badrocs = options.badrocs
badrocs = Badrocs.split(',')
if badrocs[0]=='17':
    badrocsFlag= False
else:
    badrocs = [int(x) for x in badrocs]
    badrocsFlag = True  
print 'Removing the following ROCs', badrocs
rocs = range(0,16)
if badrocsFlag:
    for x in badrocs:
        rocs.remove(x)
output = options.outputfile
material2 = 'Ag'
material3 = 'Sn'
material4 = 'In'
hist1 = histname+"_"+material1+"_C"
hist2 = histname+"_"+material2+"_C"
hist3 = histname+"_"+material3+"_C"
hist4 = histname+"_"+material4+"_C"
gROOT.SetBatch(kTRUE)
Arraytgt1 = FitPeaks(rootfile1,hist1,material1,rocs,output, XRSource, 1)
Arraytgt2 = FitPeaks(rootfile2,hist2,material2,rocs,output,XRSource, 1)
Arraytgt3 = FitPeaks(rootfile3,hist3,material3,rocs,output,XRSource, 1)
Arraytgt4 = FitPeaks(rootfile4,hist4,material4,rocs,output,XRSource, 1)
PlotSameNStats(Arraytgt1,Arraytgt2,Arraytgt3,Arraytgt4,rocs,output,XRSource)
ConversionPlot(rocs, badrocs, output,XRSource)















