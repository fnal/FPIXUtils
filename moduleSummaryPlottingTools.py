#!/usr/bin/env python
from ROOT import *
from componentTrackingTools import *
from array import array
import collections
import re
import os

# true dimensions of a sensor in 10^-4 m (active area + periphery)
PERIPHERY = 12.  # 1.2 mm
ZOOM = 5  # integer value to upscale canvas size
ROC_SIZE = ZOOM * 81.  # 8.1 mm
SENSOR_WIDTH  = 8 * ROC_SIZE
SENSOR_HEIGHT = 2 * ROC_SIZE
PLOT_UNIT = 50. # fill plots in 50 um width bins
X_UNIT = int(150./PLOT_UNIT)
Y_UNIT = int(100./PLOT_UNIT)
# ROCs have 52 columns (x) and 80 rows (y)
N_COLS = 52
N_ROWS = 80
# ROC plots are 162 wide by 162 high in 50 um units
ROC_PLOT_SIZE = X_UNIT * 50 + 2 * (2 * X_UNIT)  # 50 normal cols + 2 wide ones
MODULE_X_PLOT_SIZE = 8 * ROC_PLOT_SIZE
MODULE_Y_PLOT_SIZE = 2 * ROC_PLOT_SIZE

###############################################################################

# BEGIN SENSOR WAFER PLOTTING UTILITIES

###############################################################################

def saveSensorWaferCanvas(wafer, inputPath, plotDictionary, zMin = None, zMax = None):

    title = inputPath.split("/")

    canvas = TCanvas(wafer,"")

    canvas.SetFillStyle(0)
    canvas.SetBorderMode(0)
    canvas.SetBorderSize(0)
    canvas.SetCanvasSize(2000, 2000)
    canvas.SetMargin(0,0,0,0)
    SetOwnership(canvas, False)  # avoid going out of scope at return statement

    n = 1./6.
    padList = [
        { type : 'TT', 'location' : [n,5*n,5*n,1]},
        { type : 'FL', 'location' : [0,n,n,1-n]},
        { type : 'LL', 'location' : [n,n,2*n,1-n]},
        { type : 'CL', 'location' : [2*n,n,3*n,1-n]},
        { type : 'CR', 'location' : [3*n,n,4*n,1-n]},
        { type : 'RR', 'location' : [4*n,n,5*n,1-n]},
        { type : 'FR', 'location' : [5*n,n,1,1-n]},
        { type : 'BB', 'location' : [n,0,5*n,n]},

        { type : 'TL', 'location' : [0,5*n,n,1]},
        { type : 'TR', 'location' : [5*n,5*n,1,1]},
        { type : 'BL', 'location' : [0,0,n,n]},
        { type : 'BR', 'location' : [5*n,0,1,n]}
    ]
    padIndices = { 
        'TT' : 1,
        'FL' : 2,
        'LL' : 3,
        'CL' : 4,
        'CR' : 5,
        'RR' : 6,
        'FR' : 7,
        'BB' : 8,

        'TL' : 9,
        'TR' : 10,
        'BL' : 11,
        'BR' : 12
    }

    canvas.Divide(12)
    for pad in range(12):
        canvas.cd(pad+1)
        location = padList[pad]['location']
        x1 = location[0]
        y1 = location[1]
        x2 = location[2]
        y2 = location[3]
        gPad.SetPad(x1,y1,x2,y2)
        gPad.SetFrameLineWidth(0)
        gPad.SetFrameLineColor(0)
        if pad in [0,7]:
            gPad.SetMargin(0.01,0.01,0.04,0.04)
        elif pad in [1,2,3,4,5,6]:
            gPad.SetMargin(0.04,0.04,0.01,0.01)
        else:
            gPad.SetMargin(0,0,0,0)
            gPad.SetFillColor(920)
            gPad.SetFrameLineColor(920)

    # color bad sensors red
    canvas.cd()
    waferGrades = produceSensorGradeDictionary("/Users/lantonel/FPIXUtils/badSensors.txt")
    if wafer in waferGrades:
        for position in waferGrades[wafer]:
            canvas.cd(position)
            gPad.SetFillColor(kRed+1)
            gPad.SetFrameLineColor(kRed+1)
            gPad.SetFrameLineWidth(5)
            plot = TH2D("","",1,0,1,1,0,1)
            plot.SetStats(False)
            plot.Draw("col a")
            gPad.Update()

    # find best z-axis range if none is specified
    if zMin is None or zMax is None:
        listOfPlots = []
        for plot in plotDictionary[wafer]:
            listOfPlots.append(plot['plot'])
        zRange = findZRange(listOfPlots)
        zMin = zRange[0]
        zMax = zRange[1]

    # draw all plots
    for plot in plotDictionary[wafer]:

        canvas.cd(padIndices[plot['position']])

        # rotate histogram according to its position on the wafer
        if plot['position'] == 'BB' or plot['position'] == 'TT':
            histo = flipSummaryPlot(plot['plot'])
        else:
            histo = rotateSummaryPlot(plot['plot'])
        histo.SetDirectory(0)
        SetOwnership(histo,False)

        # turn it gray if it's going to be empty, to show that sensor has been used
        if histo.GetBinContent(histo.GetMaximumBin()) <= zMin or histo.GetBinContent(histo.GetMinimumBin()) > zMax:
            gPad.SetFillColor(920)
            gPad.SetFrameLineColor(920)
        histo.SetMinimum(zMin)
        histo.SetMaximum(zMax)
        histo.SetTitle("")
        histo.SetStats(False)
        histo.Draw('cola a')
        gPad.Update()
        canvas.Update()

    # draw wafer box in bottom left
    canvas.cd(padIndices['TL'])
    waferBox = TPaveText(0, 0, 1, 1, "NDC NB")
    waferBox.SetFillStyle(0)
    waferBox.SetFillColor(0)
    waferBox.SetTextAlign(22)
    waferBox.SetTextFont(42)
    waferBox.SetBorderSize(0)
    waferBox.AddText("Wafer")
    waferBox.AddText(wafer)
    waferBox.Draw()

    # draw plot title box in bottom left
    canvas.cd(padIndices['BL'])
    titleBox = TPaveText(0, 0, 1, 1, "NDC NB")
    titleBox.SetFillStyle(0)
    titleBox.SetFillColor(0)
    titleBox.SetTextAlign(22)
    titleBox.SetTextFont(42)
    titleBox.SetBorderSize(0)
    titleBox.AddText(title[0]+":")
    titleBox.AddText(title[1])
    titleBox.Draw()

    # draw z-scale in bottom right
    canvas.cd(padIndices['BR'])
    palette = TPaletteAxis(0.3, 0.1, 0.5, 0.9, histo)
    palette.SetLabelSize(0.1)
    palette.Draw()

    canvas.SaveAs("SensorWafer_"+wafer+"_"+inputPath.replace("/","_")+".png")


###############################################################################

# BEGIN ROC WAFER PLOTTING UTILITIES

###############################################################################

def saveROCWaferCanvas(wafer, inputPath, plotDictionary, zMin = None, zMax = None):

    title = inputPath.split("/")

    canvas = TCanvas(wafer,"")

    canvas.SetFillStyle(0)
    canvas.SetBorderMode(0)
    canvas.SetBorderSize(0)
    canvas.SetCanvasSize(2000, 2000)
    canvas.SetMargin(0,0,0,0)
    SetOwnership(canvas, False)  # avoid going out of scope at return statement

    rows = 8
    cols = 10
    canvas.Divide(cols,rows,0,0)

    # one pad per reticle
    for pad in range(rows*cols):
        canvas.cd(pad+1)
        gPad.SetMargin(0,0,0,0)
        gPad.SetBorderMode(0)
        gPad.SetBorderSize(0)
        gPad.Divide(2,2,0,0)
        # one subpad per ROC
        for subpad in range(4):
            canvas.cd(pad+1)
            gPad.cd(subpad+1)
            # eyeballed this to make them square-ish
            # and account for periphery on bottom edge
            gPad.SetMargin(0.02,0.02,0.2,0.02)
            gPad.SetFillStyle(1001)
            gPad.SetBorderMode(0)
            gPad.SetBorderSize(0)
            gPad.Update()

    emptyReticles = [1,2,3,9,10,11,20,21,51,61,62,70,71,72,73,74,78,79,80]

    for pad in emptyReticles:
        canvas.cd(pad)
        gPad.SetFillColor(920)
        gPad.SetFrameLineColor(920)
        gPad.SetFillStyle(1001)
        plot = TH2D("","",1,0,1,1,0,1)
        plot.SetStats(False)
        plot.Draw("col a")
        gPad.Update()

    colors = [kWhite,kBlue+1,kViolet+1,kYellow+1,kRed+1]
    canvas.cd()
    waferGrades = produceROCGradeDictionary(wafer)
    for roc,grade in waferGrades.iteritems():
        position = roc.split('-')[1]
        pad = int(position[0]) * 10 + int(position[1]) + 1
        subpad = ord(position[2]) - ord('A') + 1
        canvas.cd(pad)
        gPad.cd(subpad)
        gPad.SetFillColor(colors[grade-1])
        gPad.SetFrameLineColor(colors[grade-1])
        gPad.SetFrameLineWidth(5)
#        gPad.SetFillStyle(1001)
        plot = TH2D("","",1,0,1,1,0,1)
        plot.SetStats(False)
        plot.Draw("col a")
        gPad.Update()

    # find best z-axis range if none is specified
    if zMin is None or zMax is None:
        listOfPlots = []
        for plot in plotDictionary[wafer]:
            listOfPlots.append(plot['plot'])
        zRange = findZRange(listOfPlots)
        zMin = zRange[0]
        zMax = zRange[1]

    # draw all plots
    for plot in plotDictionary[wafer]:
        canvas.cd(plot['pad'])
        gPad.cd(plot['subpad'])
        gPad.SetFillColor(0)
        histo = plot['plot']
        # turn it gray if it's going to be empty, to show that ROC has been used
        if histo.GetBinContent(histo.GetMaximumBin()) <= zMin or histo.GetBinContent(histo.GetMinimumBin()) > zMax:
            gPad.SetFillColor(920)
            gPad.SetFrameLineColor(920)
        histo.SetMinimum(zMin)
        histo.SetMaximum(zMax)
        histo.SetTitle("")

        histo.SetStats(False)
        histo.Draw('cola a')

    canvas.cd()

    # draw labels and lines
    width = 0.03
    height = 0.03
    line = TLine()
    line.SetLineColor(920)
    line.SetLineWidth(3)

    for x in range(cols):
        x_center = (1 + 2*x) * 1./(2*cols)
        y_center = 1 - height/2.
        label = TPaveText(x_center - width/2., y_center - height/2., x_center + width/2.,  y_center + height/2., "NDC NB")
        label.AddText("Y"+ str(x))
        label.SetFillStyle(0)
        label.SetFillColor(0)
        label.SetTextAlign(22)
        label.SetTextFont(42)
        label.SetBorderSize(0)
        label.Draw()
        SetOwnership(label,False)  # avoid going out of scope at return statement

        # draw vertical lines
        line.DrawLine((x+1)/float(cols),0,(x+1)/float(cols),1)

    for y in range(rows):
        x_center = width/2
        y_center = (1 + 2*y) * 1./(2*rows)
        label = TPaveText(x_center - width/2., y_center - height/2., x_center + width/2.,  y_center + height/2., "NDC NB")
        label.AddText(str(rows - y - 1) + "X")
        label.SetFillStyle(0)
        label.SetFillColor(0)
        label.SetTextAlign(22)
        label.SetTextFont(42)
        label.SetBorderSize(0)
        label.Draw()
        SetOwnership(label,False)  # avoid going out of scope at return statement

        # draw horizontal lines
        line.DrawLine(0,(y+1)/float(rows),1,(y+1)/float(rows))

    # draw wafer box in bottom left
    waferBox = TPaveText(0.1, 0, 0.4, 1./8., "NDC NB")
    waferBox.SetFillStyle(0)
    waferBox.SetFillColor(0)
    waferBox.SetTextAlign(22)
    waferBox.SetTextFont(42)
    waferBox.SetBorderSize(0)
    waferBox.AddText(wafer)
    waferBox.Draw()

    # draw plot title box in bottom right
    titleBox = TPaveText(0.7, 0, 0.9, 1./8., "NDC NB")
    titleBox.SetFillStyle(0)
    titleBox.SetFillColor(0)
    titleBox.SetTextAlign(22)
    titleBox.SetTextFont(42)
    titleBox.SetBorderSize(0)
    titleBox.AddText(title[0]+":")
    titleBox.AddText(title[1])
    titleBox.Draw()

    # draw z-scale in bottom right
    palette = TPaletteAxis(0.91,0.02,0.94,2./8.-0.02,plotDictionary[wafer][0]['plot'])
    palette.SetLabelSize(0.025)
    palette.Draw()

    canvas.SaveAs("ROCWafer_"+wafer+"_"+inputPath.replace("/","_")+".png")


###############################################################################

# BEGIN MODULE SUMMARY PLOTTING UTILITIES

###############################################################################


###############################################################################

# function to process the 16 histograms and flip bin contents of the top half
# input a set of histograms and return a flipped version of the top ones
def flipTopRow(plots):

    for roc in range(8):
        histo = plots[roc].Clone()
        histo.SetDirectory(0)
        histo.Reset()
        nBinsX = histo.GetNbinsX()
        nBinsY = histo.GetNbinsY()
        for x in range(1,nBinsX+1):
            for y in range(1, nBinsY+1):
                content = plots[roc].GetBinContent(x,y)
                error   = plots[roc].GetBinError(x,y)
                if plots[roc].ClassName() == "TProfile2D":
                    histo.Fill(nBinsX-x, nBinsY-y, content)
                else:
                    histo.SetBinContent(nBinsX-x+1, nBinsY-y+1, content)
                    histo.SetBinError(nBinsX-x+1, nBinsY-y+1, error)

        plots[roc] = histo

###############################################################################

# function to rotate a module summary plot by 180 degrees
def flipSummaryPlot(plot):

    histo = plot.Clone()
    histo.SetDirectory(0)
    histo.Reset()
    nBinsX = histo.GetNbinsX()
    nBinsY = histo.GetNbinsY()
    for x in range(1,nBinsX+1):
        for y in range(1, nBinsY+1):
            content = plot.GetBinContent(x,y)
            error   = plot.GetBinError(x,y)
            histo.SetBinContent(nBinsX-x+1, nBinsY-y+1, content)
            histo.SetBinError(nBinsX-x+1, nBinsY-y+1, error)

    return histo

###############################################################################

# function to rotate a module summary plot clockwise by 90 degrees
def rotateSummaryPlot(plot):
    name = plot.GetName()
    title = plot.GetTitle()
    nBinsX = plot.GetNbinsX()
    nBinsY = plot.GetNbinsY()
    binEdgesX = []
    binEdgesY = []
    for bin in range(nBinsX+1):
        binEdgesX.append(int(plot.GetXaxis().GetBinLowEdge(bin+1)))
    for bin in range(nBinsY+1):
        binEdgesY.append(int(plot.GetYaxis().GetBinLowEdge(bin+1)))
    histo = plot.Clone()
    histo.SetDirectory(0)
    histo.Reset()
    histo.SetBins(len(binEdgesY)-1,
                  array('d',binEdgesY),
                  len(binEdgesX)-1,
                  array('d',binEdgesX))
    for x in range(1,nBinsX+1):
        for y in range(1, nBinsY+1):
            content = plot.GetBinContent(x,y)
            error   = plot.GetBinError(x,y)
            histo.SetBinContent(y, nBinsX-x+1, content)
            histo.SetBinError(y, nBinsX-x+1, content)

    return histo


###############################################################################

# Input 16 plots (one per ROC) and return one merged plot with variable bins
# fill in units of 50um to account for larger edge pixels
def makeMergedPlot(plots):

    flipTopRow(plots)

    # x bins are units of 150um (except for bigger edge pixels)
    rocBinEdgesX = [0]
    for x in range(0,X_UNIT*(N_COLS-1),X_UNIT):
        rocBinEdgesX.append(x+2*X_UNIT) # first bin is twice as wide

    # y bins are units of 100um (except for bigger edge pixels)
    rocBinEdgesY = [0]
    for y in range(0,Y_UNIT*(N_ROWS-1),Y_UNIT):
        rocBinEdgesY.append(y+Y_UNIT)

    # we want to create a plot that's 8x2 ROCs

    moduleBinEdgesX = []
    for roc in range(8):  # 0 - 7
        for edge in rocBinEdgesX:
            moduleBinEdgesX.append(edge + ROC_PLOT_SIZE*roc)
    moduleBinEdgesX.append(8 * ROC_PLOT_SIZE)  # add final bin by hand

    moduleBinEdgesY = []
    # add bottom row of rocs
    for edge in rocBinEdgesY:
        moduleBinEdgesY.append(edge)
    # add top row of rocs
    moduleBinEdgesY.append(ROC_PLOT_SIZE)  # add last bin by hand
    for edge in reversed(rocBinEdgesY):
        moduleBinEdgesY.append(2 * ROC_PLOT_SIZE - edge)

    # create clone of plot with new bin sizes
    plotName = plots[0].GetName().rstrip("0")
    summaryPlot = TH2D(plotName,
                       "",
                       len(moduleBinEdgesX)-1,
                       array('d',moduleBinEdgesX),
                       len(moduleBinEdgesY)-1,
                       array('d',moduleBinEdgesY))
    summaryPlot.SetStats(False)
    summaryPlot.SetDirectory(0)

    # fill new histogram with contents of original plots
    # put ROC 0 at the top right, because reason

    # fill bottom row first
    for roc in range(8,16):
        plot = plots[roc]

        for x in range(1,plot.GetNbinsX()+1):
            for y in range(1,plot.GetNbinsY()+1):
                content = plot.GetBinContent(x,y)
                error = plot.GetBinError(x,y)
                summaryPlot.SetBinContent(x+N_COLS*(roc-8),y,content)
                summaryPlot.SetBinError(x+N_COLS*(roc-8),y,error)

    # fill top row second
    for roc in range(7,-1,-1):  # loop backwards so 0 is last
        plot = plots[roc]

        for x in range(1,plot.GetNbinsX()+1):
            for y in range(1,plot.GetNbinsY()+1):
                content = plot.GetBinContent(x,y)
                error = plot.GetBinError(x,y)
                summaryPlot.SetBinContent(x+N_COLS*(7-roc),y+N_ROWS,content)
                summaryPlot.SetBinError(x+N_COLS*(7-roc),y+N_ROWS,error)

    return summaryPlot

###############################################################################

# gets the global min and max
# for each ROC, finds mean & RMS
# sets global range according to global min and max
# ignores any points outside a nSigma window around the ROC mean
# returns zmin and zmax
def findZRange(plots):
    zMax = -999
    zMin = 999
    nSigma = 3
    globalMin = 0.00002

    for roc in range(len(plots)):
        plot = plots[roc].Clone()

        # don't consider empty plots from dead ROCs
        if not plot.GetMaximum() and not plot.GetMinimum():
#            print "found empty plot:", plot.GetName()
            continue

        # treat special cases first - don't alter range
        if "PixelAlive" in plot.GetName() or \
           "MaskTest" in plot.GetName() or \
           "AddressDecodingTest" in plot.GetName():
            # avoid empty ROCs screwing up the range
            if plot.GetMinimum() != plot.GetMaximum():
                return(plot.GetMinimum(),plot.GetMaximum())
            continue

        if "rescaledThr" in plot.GetName():
            rocMin = plot.GetMinimum() - 0.00001
        else:
            rocMin = max(plot.GetMinimum(), globalMin) - 0.00001
        rocMax = plot.GetMaximum() + 0.00001
        # create 1D distribution to get mean, RMS
        oneDPlot = TH1F("1d","1d",10000,rocMin,rocMax)
        for x in range(1,plot.GetNbinsX()+1):
            for y in range(1,plot.GetNbinsY()+1):
                content = plot.GetBinContent(x,y)
                # ignore empty bins
                if content == 0:
                    continue
                # remove things close to -2 (failed s-curve thr)
                if abs(content + 2) < 0.01:
                    continue
                oneDPlot.Fill(content)

        mean = oneDPlot.GetMean()
        sigma = oneDPlot.GetRMS()
        plotMin = mean - nSigma*sigma
        plotMax = mean + nSigma*sigma
        oneDPlot.Delete()

        NBINS = 10000
        # create zoomed 1D distribution to find normally distributed dataset
        oneDPlotZoomed = TH1F("1d","1d",NBINS,plotMin,plotMax)
        for x in range(1,plot.GetNbinsX()+1):
            for y in range(1,plot.GetNbinsY()+1):
                content = plot.GetBinContent(x,y)
                if content < plotMin or content > plotMax or content < rocMin:
                    continue
                # ignore empty bins
                if content == 0:
                    continue
                # remove things close to -2 (failed s-curve thr)
                if abs(content + 2) < 0.01:
                    continue
                oneDPlotZoomed.Fill(content)

        mean = oneDPlotZoomed.GetMean()
        sigma = oneDPlotZoomed.GetRMS()
        oneDPlotZoomed.Delete()
        plotMin = mean - nSigma*sigma
        plotMax = mean + nSigma*sigma


        binWidth = (plotMax - plotMin)/float(NBINS)
        # create groomed 1D distribution to find min/max filled bins
        oneDPlotGroomed = TH1F("1d","1d",NBINS,plotMin,plotMax)
        for x in range(1,plot.GetNbinsX()+1):
            for y in range(1,plot.GetNbinsY()+1):
                content = plot.GetBinContent(x,y)
                if content < plotMin and content > plotMax or content < rocMin:
                    continue
                # ignore empty bins
                if content == 0:
                    continue
                # remove things close to -2 (failed s-curve thr)
                if abs(content + 2) < 0.01:
                    continue
                oneDPlotGroomed.Fill(content)

        # get position of first and last bins with non-zero entries
        rocMin = oneDPlotGroomed.GetBinLowEdge(oneDPlotGroomed.FindFirstBinAbove()) + binWidth
        rocMax = oneDPlotGroomed.GetBinLowEdge(oneDPlotGroomed.FindLastBinAbove())

        oneDPlotGroomed.Delete()

        if rocMax > zMax:
            zMax = rocMax
        if rocMin < zMin:
            zMin = rocMin

    # round to nearest integer before returning
    return (floor(zMin), ceil(zMax))

###############################################################################

# pass this function a plot and a list with two elements - [zMin,zMax]
def setZRange(plot, range):

    plot.SetMinimum(range[0])
    plot.SetMaximum(range[1])

###############################################################################

# input a summary merged plot and draw it on a canvas
# add axis ticks and labels
# return canvas
def setupSummaryCanvas(summaryPlot):

    pathToHistogram = summaryPlot.GetName()
    splitPath = pathToHistogram.split("/")
    plotName = splitPath[-1].split("_Summary")[0]
    if len(splitPath) > 1:
        dirName = splitPath[0]
    else:
        dirName = None

    summaryPlot.SetName(plotName)
    canvas = TCanvas(plotName,"")


    # use numbers that are factors of ROC_SIZE to avoid rounding errors
    # dirName will be empty in the MoReWeb case
    if dirName is not None:
        topMargin = ROC_SIZE
    else:
        topMargin = 2 * ROC_SIZE/3.
    bottomMargin = 2 * ROC_SIZE/3.
    leftMargin = 2 * ROC_SIZE/3.
    rightMargin = 2 * ROC_SIZE

    canvas.SetBorderMode(0)
    canvas.SetBorderSize(0)
    canvasWidth = int(SENSOR_WIDTH + leftMargin + rightMargin)
    canvasHeight = int(SENSOR_HEIGHT + topMargin + bottomMargin)
    canvas.SetCanvasSize(canvasWidth, canvasHeight)
    canvas.SetFixedAspectRatio()
    SetOwnership(canvas, False)  # avoid going out of scope at return statement

    gPad.SetBorderMode(0)
    gPad.SetBorderSize(0)
    gPad.SetLeftMargin(leftMargin/canvasWidth)
    gPad.SetRightMargin(rightMargin/canvasWidth)
    gPad.SetTopMargin(topMargin/canvasHeight)
    gPad.SetBottomMargin(bottomMargin/canvasHeight)

    summaryPlot.Draw("colz a") # in color (without axes)
    SetOwnership(summaryPlot, False)  # avoid going out of scope at return statement

    canvas.Update()
    palette = summaryPlot.GetListOfFunctions().FindObject("palette")
    palette.SetX1NDC((canvasWidth-2*rightMargin/3.)/canvasWidth)
    palette.SetX2NDC((canvasWidth-rightMargin/2.)/canvasWidth)
    palette.SetY1NDC(0.05)
    palette.SetY2NDC(0.95)
    palette.SetLabelSize(0.06)
    palette.SetLabelFont(42)

    # START ADDING AXES

    tickLength = 7
    textBoxWidth = 20
    axisLabels = []

    # x-axis ticks
    x_start = 0

    # 8 ROCS
    for roc in range(8):
        # 5 ticks per ROC - at 0,10,20,30,40
        xoffset = 0
        for i in range(5):
            if i is 1:
                xoffset += 10 * X_UNIT + X_UNIT  # account for wider edge pixel
            elif i > 1:
                xoffset += 10 * X_UNIT
            x1 = x_start+xoffset
            x2 = (MODULE_X_PLOT_SIZE-x_start)-xoffset

            text1 = TPaveText(x1-textBoxWidth/2.,
                              -1*(tickLength + textBoxWidth + 5),
                              x1+textBoxWidth/2.,
                              -1*(tickLength + 5),
                              "NB")
            text1.AddText(str(10*i))
            axisLabels.append(text1)

            text2 = TPaveText(x2-textBoxWidth/2.,
                              MODULE_Y_PLOT_SIZE + tickLength + textBoxWidth + 5,
                              x2+textBoxWidth/2.,
                              MODULE_Y_PLOT_SIZE + tickLength + 5,
                              "NB")
            text2.AddText(str(10*i))
            axisLabels.append(text2)

            line1 = TLine()
            line2 = TLine()
            rocBoundaryLine = TLine()
            rocBoundaryLine.SetLineStyle(2)
            if i is 0:
                line1.DrawLine(x1,
                               tickLength/5.,
                               x1,
                               -2*tickLength)
                line2.DrawLine(x2,
                               MODULE_Y_PLOT_SIZE - tickLength/5.,
                               x2,
                               MODULE_Y_PLOT_SIZE + 2*tickLength)
                if roc is not 0:  # no vertical line at left module edge
                    rocBoundaryLine.DrawLine(x1,
                                             0,
                                             x1,
                                             MODULE_Y_PLOT_SIZE)
            else:
                line1.DrawLine(x1,
                               tickLength/5.,
                               x1,
                               -1*tickLength)
                line2.DrawLine(x2,
                               MODULE_Y_PLOT_SIZE - tickLength/5.,
                               x2,
                               MODULE_Y_PLOT_SIZE + 1*tickLength)

        # move to next ROC
        x_start += ROC_PLOT_SIZE

    rocBoundaryLine = TLine()
    rocBoundaryLine.SetLineStyle(2)
    rocBoundaryLine.DrawLine(0,
                             MODULE_Y_PLOT_SIZE/2.,
                             MODULE_X_PLOT_SIZE,
                             MODULE_Y_PLOT_SIZE/2.)

    # y-axis ticks
    # this should be easier since 80 is divisible by 10
    y_offset = 0
    for tick in range(17):

        text1 = TPaveText(-1*(tickLength + textBoxWidth + 5),
                          y_offset - textBoxWidth/2.,
                          -1*(tickLength + 5),
                          y_offset + textBoxWidth/2.,
                          "NB")
        text2 = TPaveText(MODULE_X_PLOT_SIZE + tickLength + 5,
                          y_offset - textBoxWidth/2.,
                          MODULE_X_PLOT_SIZE + tickLength + textBoxWidth + 5,
                          y_offset + textBoxWidth/2.,
                          "NB")

        if tick < 8:
            text1.AddText(str(10*tick))
            text2.AddText(str(10*tick))
        else:
            text1.AddText(str(160-10*tick))
            text2.AddText(str(160-10*tick))

        axisLabels.append(text1)
        axisLabels.append(text2)

        line1 = TLine()
        line2 = TLine()
        if tick % 8 is 0:
            line1.DrawLine(0,
                           y_offset,
                           -2 * tickLength,
                           y_offset)
            line2.DrawLine(MODULE_X_PLOT_SIZE,
                           y_offset,
                           2 * tickLength + MODULE_X_PLOT_SIZE,
                           y_offset)
        else:
            line1.DrawLine(0,
                           y_offset,
                           -1 * tickLength,
                           y_offset)
            line2.DrawLine(MODULE_X_PLOT_SIZE,
                           y_offset,
                           1 * tickLength + MODULE_X_PLOT_SIZE,
                           y_offset)
        if tick is 7 or tick is 8:
            y_offset += 10 * Y_UNIT + Y_UNIT  # account for larger edge pixels
        else:
            y_offset += 10 * Y_UNIT


    # roc labels for bottom row
    for roc in range(8):
        rocLabel = TPaveText(ROC_PLOT_SIZE/2. + ROC_PLOT_SIZE*roc - textBoxWidth*2,
                          -(4*textBoxWidth),
                          ROC_PLOT_SIZE/2. + ROC_PLOT_SIZE*roc + textBoxWidth*2,
                          -(2*textBoxWidth),
                          "NB")
        rocLabel.AddText("C"+str(roc+8))
        axisLabels.append(rocLabel)

    # roc labels for top row
    for roc in range(8):
        rocLabel = TPaveText(ROC_PLOT_SIZE/2. + ROC_PLOT_SIZE*roc - textBoxWidth*2,
                             (4*textBoxWidth) + MODULE_Y_PLOT_SIZE,
                             ROC_PLOT_SIZE/2. + ROC_PLOT_SIZE*roc + textBoxWidth*2,
                             (2*textBoxWidth) + MODULE_Y_PLOT_SIZE,
                             "NB")
        rocLabel.AddText("C"+str(7 -roc))
        axisLabels.append(rocLabel)

    for label in axisLabels:

        label.SetFillColor(0)
        label.SetTextAlign(22)
        label.SetTextFont(42)
        label.SetBorderSize(0)
        label.Draw()
        SetOwnership(label,False)  # avoid going out of scope at return statement

    title = TPaveText(leftMargin/canvasWidth,
                      (SENSOR_HEIGHT + bottomMargin + 0.6*topMargin)/canvasHeight,
                      (SENSOR_WIDTH + leftMargin)/canvasWidth,
                      (SENSOR_HEIGHT + bottomMargin + 0.95*topMargin)/canvasHeight,
                      "NDC NB")
    if dirName is not None:
        title.AddText(dirName + ": " + plotName)
    title.SetFillColor(0)
    title.SetTextAlign(22)
    title.SetTextFont(42)
    title.SetBorderSize(0)

    title.Draw()
    SetOwnership(title,False)  # avoid going out of scope at return statement

    return canvas

###############################################################################

def saveCanvasToNewFile(canvas,outputFileName):

    outputFile = TFile(outputFileName, "RECREATE")
    outputFile.cd()
    canvas.Write()
    outputFile.Close()

###############################################################################

def produce1DDistributions(inputFileName, pathToHistogram, version=0):

    inputFile = TFile(inputFileName)
    plots = []

    # get plots
    for roc in range(16):
        plotPath = pathToHistogram + "_C" + str(roc) + "_V" + str(version)
        if not inputFile.Get(plotPath):
            print "missing plot:", plotPath
            continue
        else:
            twoDplot = inputFile.Get(plotPath).Clone()

        oneDplotName = "dist_"+twoDplot.GetName()
        # we'll assume we're plotting an 8-bit DAC value,
        # expect for a couple of explicit exceptions
        if "_sig_" in oneDplotName:
            oneDplot = TH1F(oneDplotName,oneDplotName,100,0,10)
        elif "_TrimMap_" in oneDplotName:
            oneDplot = TH1F(oneDplotName,oneDplotName,16,0,16)
        else:
            oneDplot = TH1F(oneDplotName,oneDplotName,256,0,256)
        oneDplot.SetDirectory(0)
        for x in range(1,twoDplot.GetNbinsX()+1):
            for y in range(1,twoDplot.GetNbinsY()+1):
                content = twoDplot.GetBinContent(x,y)
                oneDplot.Fill(content)
        plots.append(oneDplot)
    return plots

###############################################################################

# recursively build list of directories in the input file
def getListOfDirectories(inputFile, list = [], directory = ''):

    inputFile.cd(directory)
    list.append(directory)
    for dirKey in gDirectory.GetListOfKeys():
        if (dirKey.GetClassName() != "TDirectoryFile"):
            continue
        dir = dirKey.GetName()
        newDirectory = directory + "/" + dir
        getListOfDirectories(inputFile, list, newDirectory)

# build list of 1D histograms in the input file
def getListOf1DHistograms(inputFile, directoryList):

    histogramList = []

    for dir in directoryList:
        inputFile.cd(dir)
        for plotKey in gDirectory.GetListOfKeys():
            if re.match ('TH1', plotKey.GetClassName()): # found a 1-D histogram
                plotName = plotKey.GetName()
                # only consider distributions made from 2D plots
                if not plotName.startswith("dist_"):
                    continue
                # ignore summary plots from previous processings
                if "Summary" in plotName:
                    continue
                pathToHistogram = dir+"/"+plotName
                plot = inputFile.Get(pathToHistogram)
                histogramList.append(pathToHistogram)

    return histogramList

# build list of 2D histograms in the input file
def getListOf2DHistograms(inputFile, directoryList):

    histogramList = []

    for dir in directoryList:
        inputFile.cd(dir)
        for plotKey in gDirectory.GetListOfKeys():
            if re.match ('TH2', plotKey.GetClassName()) or \
               re.match ('TProfile2', plotKey.GetClassName()): # found a 2-D plot
                plotName = plotKey.GetName()
                pathToHistogram = dir+"/"+plotName
                plot = inputFile.Get(pathToHistogram)
                # only consider ROC summary plots
                if plot.GetNbinsX() != 52 or plot.GetNbinsY() != 80:
                    continue
                histogramList.append(pathToHistogram)

    return histogramList

# look through an input file (presumably a pxar output file)
# find all roc summary plots and return a list of them
def produce2DHistogramDictionary(inputFileName, mode = 'pxar'):

    directoryList = []

    inputFile = TFile(inputFileName)

    getListOfDirectories(inputFile, directoryList)
    histogramList = getListOf2DHistograms(inputFile, directoryList)

    inputFile.Close()

    # dictionary of histogram names, each entry containing the versions present
    histogramDictionary = collections.OrderedDict()
    for histogram in histogramList:

        if mode == 'pxar':
            version = histogram[-1:]
            chipIndex = histogram.rfind("_C")
        else:
            version = '0'
            chipIndex = histogram.rfind("_ROC")
        histoName = histogram[:chipIndex]
        # if it's not already in the list, add it
        if not histoName in histogramDictionary:
            histogramDictionary[histoName] = []
            histogramDictionary[histoName].append(version)
        # if it's there but this is a new version, add this version
        else:
            if not version in histogramDictionary[histoName]:
                histogramDictionary[histoName].append(version)
    return histogramDictionary

###############################################################################

# look through an input file (presumably a pxar output file)
# find all roc summary 1D distributions and return a list of them
def produce1DHistogramDictionary(inputFileName, mode = 'pxar'):

    directoryList = []

    inputFile = TFile(inputFileName)

    getListOfDirectories(inputFile, directoryList)
    histogramList = getListOf1DHistograms(inputFile, directoryList)

    inputFile.Close()

    # dictionary of histogram names, each entry containing the versions present
    histogramDictionary = collections.OrderedDict()
    for histogram in histogramList:

        if mode == 'pxar':
            version = histogram[-1:]
            chipIndex = histogram.rfind("_C")
        else:
            version = '0'
            chipIndex = histogram.rfind("_ROC")
        histoName = histogram[:chipIndex]
        # if it's not already in the list, add it
        if not histoName in histogramDictionary:
            histogramDictionary[histoName] = []
            histogramDictionary[histoName].append(version)
        # if it's there but this is a new version, add this version
        else:
            if not version in histogramDictionary[histoName]:
                histogramDictionary[histoName].append(version)
    return histogramDictionary


###############################################################################

def add2DSummaryPlots(inputFileName, histogramDictionary, mode = 'pxar', savePlots = False):

    if savePlots:
        outputDir = inputFileName.split(".root")[0] + "_2DModuleSummaryPlots"
        if not os.path.isdir(outputDir):
            os.mkdir(outputDir)

    for histoName, versions in histogramDictionary.items():
        for version in versions:
            summaryPlot = produce2DSummaryPlot(inputFileName,histoName,version,mode)
            if summaryPlot is None:
                continue
            directory = histoName.rsplit("/", 1)[0]
            inputFile = TFile(inputFileName, "UPDATE")
            inputFile.cd(directory)
            gDirectory.Delete(summaryPlot.GetName()+";*")  # remove duplicates
            print "adding 2D summary plot: "+directory+"/"+summaryPlot.GetName()
            summaryPlot.Write()
            if savePlots:
                outputFileName = directory + "_" + summaryPlot.GetName() + ".png"
                summaryPlot.SaveAs(outputDir + "/" + outputFileName)
            inputFile.Close()

###############################################################################

def add1DSummaryPlots(inputFileName, histogramDictionary, mode = 'pxar'):

    for histoName, versions in histogramDictionary.items():
        for version in versions:
            summaryPlot = produce1DSummaryPlot(inputFileName,histoName,version,mode)
            if summaryPlot is None:
                continue
            directory = histoName.rsplit("/", 1)[0]
            inputFile = TFile(inputFileName, "UPDATE")
            inputFile.cd(directory)
            gDirectory.Delete(summaryPlot.GetName()+";*")  # remove duplicates
            print "adding 1D summary plot: "+directory+"/"+summaryPlot.GetName()
            summaryPlot.Write()
            inputFile.Close()

###############################################################################

def add1DDistributions(inputFileName, histogramDictionary):

    for histoName, versions in histogramDictionary.items():
        for version in versions:
            distributions = produce1DDistributions(inputFileName,histoName,version)
            directory = histoName.rsplit("/", 1)[0]
            inputFile = TFile(inputFileName, "UPDATE")
            inputFile.cd(directory)
            for distribution in distributions:
                # if the plot's already there, don't mess with it
                existingPlot = gDirectory.Get(distribution.GetName())
                if existingPlot:
                    continue
                print "adding 1D distribution: "+directory+"/"+distribution.GetName()
                distribution.Write()
            inputFile.Close()

###############################################################################

# pass in the input file and location of relevant histogram
# return the canvas with the finished summary plot
def produce2DSummaryPlot(inputFileName, pathToHistogram, version=0, mode='pxar', zRange=()):

    plots = produce2DPlotList(inputFileName, pathToHistogram, version, mode)
    summaryPlot = makeMergedPlot(plots)
    if not zRange: zRange = findZRange(plots)
    setZRange(summaryPlot,zRange)
    summaryCanvas = setupSummaryCanvas(summaryPlot)

    return summaryCanvas

###############################################################################

# pass in the input file and location of relevant histogram
# return the list of 16 ROC plots
def produce2DPlotList(inputFileName, pathToHistogram, version=0, mode='pxar'):

    inputFile = TFile(inputFileName)
    plots = []
    foundPlot = False

    # get plots
    for roc in range(16):
        if mode == 'pxar':
            plotPath = pathToHistogram + "_C" + str(roc) + "_V" + str(version)
        else:
            plotPath = pathToHistogram + "_ROC" + str(roc)
        if not inputFile.Get(plotPath):
            print "missing plot:", plotPath
            plot = TH2D("","",52,0,52,80,0,80)  # insert empty plot
        else:
            foundPlot = True
            plot = inputFile.Get(plotPath).Clone()
        plotName = pathToHistogram.lstrip("/")
        if mode == 'pxar':
            plot.SetName(plotName + "_V" + str(version) + "_Summary" + str(roc))
        else:
            plot.SetName(plotName + "_Summary" + str(roc))
        plot.SetDirectory(0)
        plots.append(plot)
    if not foundPlot:
        print "no valid plots found, skipping"
        return None

    return plots

###############################################################################

# takes a set of 16 ROC plots
# replaces the contents of each bin with 1 (true) or 0 (false) depending on
# whether it falls within the provided range (inclusive)
def makeBinaryPlots(plots, min=0, max=1):

    # decide whether to include a range or veto a range
    vetoRange = False
    if max < min:
        vetoRange = True

    for roc in range(16):

        histo = plots[roc].Clone()
        histo.SetDirectory(0)
        histo.Reset()
        nBinsX = histo.GetNbinsX()
        nBinsY = histo.GetNbinsY()
        for x in range(1,nBinsX+1):
            for y in range(1, nBinsY+1):
                content = plots[roc].GetBinContent(x,y)
                if plots[roc].GetEntries() == 0:
                    histo.SetBinContent(x, y, 0)
                elif not vetoRange and (content >= min and content <= max):
                    histo.SetBinContent(x, y, 1)
                elif vetoRange and (content >= min or content <= max):
                    histo.SetBinContent(x, y, 1)
                else:
                    histo.SetBinContent(x, y, 0)
        plots[roc] = histo


###############################################################################

# takes a set of 16 ROC plots
# returns the sum of them all
def makeSumPlot(plots):

    histo = plots[0].Clone()
    for roc in range(1,16):
        histo.Add(plots[roc])

    return histo

###############################################################################

# pass in the input file and location of relevant histogram
# return the list of 16 ROC plots
def produce1DPlotList(inputFileName, pathToHistogram, version=0, mode='pxar'):

    inputFile = TFile(inputFileName)
    plots = []
    foundPlot = False

    # get plots
    for roc in range(16):
        if mode == 'pxar':
            plotPath = pathToHistogram + "_C" + str(roc) + "_V" + str(version)
        else:
            plotPath = pathToHistogram + "_ROC" + str(roc)
        if not inputFile.Get(plotPath):
            print "missing plot:", plotPath
            plot = TH1D("","",256,0,256)  # insert empty plot
        else:
            foundPlot = True
            plot = inputFile.Get(plotPath).Clone()
        plot.SetDirectory(0)
        plots.append(plot)
    if not foundPlot:
        print "no valid plots found, skipping"
        return None

    return plots

###############################################################################

# pass in the input file and location of relevant histogram
# return merged 1D summary plot
def produce1DSummaryPlot(inputFileName, pathToHistogram, version=0, mode='pxar'):

    plots = produce1DPlotList(inputFileName, pathToHistogram, version, mode)

    summaryPlot = plots[0].Clone()
    summaryPlot.SetDirectory(0)
    if mode == 'pxar':
        chipIndex = summaryPlot.GetName().rfind("_C")
    else:
        chipIndex = summaryPlot.GetName().rfind("_ROC")
    newName = summaryPlot.GetName()[:chipIndex]
    if mode == 'pxar':
        summaryPlot.SetName(newName + "_V" + str(version) + "_Summary")
    else:
        summaryPlot.SetName(newName + "_Summary")
    oldTitle = summaryPlot.GetTitle()
    if "(C" in oldTitle:
        chipIndex = oldTitle.rfind("(C")
        versionIndex = oldTitle.rfind("(V")
    else:
        chipIndex = oldTitle.rfind("_C")
        versionIndex = oldTitle.rfind("_V")
    newTitle1 = oldTitle[:chipIndex]
    newTitle2 = oldTitle[versionIndex:]
    summaryPlot.SetTitle(newTitle1 + newTitle2)
    for roc in range(1,16):
        summaryPlot.Add(plots[roc])

#    functions = []
#    for function in summaryPlot.GetListOfFunctions():
#        functions.append(function)
#    for function in functions:
#        if function.InheritsFrom('TArrow'):
#            print function
#            function.Delete()
#            print "deleted"

    return summaryPlot

###############################################################################

# temporary altered version of produceSummaryPlot for use in lessWeb.py
def produceLessWebSummaryPlot(inputFile, pathToHistogram, outputDir, zRange=(), isBB3=False, version=0):

    summaryCanvas=produce2DSummaryPlot(inputFile.GetName(), pathToHistogram, zRange=zRange)

    if summaryPlot is None:
        continue

    if isBB3 and zRange:
        colors = array("i",[51+i for i in range(40)] + [kRed])
        gStyle.SetPalette(len(colors), colors);
        zMin=zRange[0]
        zMax=zRange[1]
        step=float(zMax-zMin)/(len(colors)-1)
        levels = array('d',[zMin + i*step for i in range(len(colors)-1)]+[4.9999999])

        summaryPlot=summaryCanvas.GetPrimitive(pathToHistogram.split("/")[-1]+'_V0')
        summaryPlot.SetContour(len(levels),levels)

    outputFileName = pathToHistogram.replace("/","_")
    summaryCanvas.SaveAs(outputDir + "/" + outputFileName + ".png")

    if isBB3 and zRange:
        colors = array("i",[51+i for i in range(50)])
        gStyle.SetPalette(len(colors), colors);
