#!/usr/bin/env python
from ROOT import *
from databaseTools.componentTrackingTools import *
from moduleSummaryPlottingTools import *
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
    # including periphery calculations
    canvas.SetCanvasSize(2232, 2088)
    canvas.SetMargin(0,0,0,0)
    SetOwnership(canvas, False)  # avoid going out of scope at return statement

    # 
    
    lowEdge = 186./1044.
    highEdge = 1. - lowEdge
    leftEdge = 0.5 - (672./2.)/1116.
    rightEdge = 0.5 + (672./2.)/1116.
    n = 1./6.
    padList = [
        { type : 'TT', 'location' : [leftEdge,highEdge,rightEdge,1]},
        { type : 'FL', 'location' : [0,lowEdge,n,highEdge]},
        { type : 'LL', 'location' : [n,lowEdge,2*n,highEdge]},
        { type : 'CL', 'location' : [2*n,lowEdge,3*n,highEdge]},
        { type : 'CR', 'location' : [3*n,lowEdge,4*n,highEdge]},
        { type : 'RR', 'location' : [4*n,lowEdge,5*n,highEdge]},
        { type : 'FR', 'location' : [5*n,lowEdge,1,highEdge]},
        { type : 'BB', 'location' : [leftEdge,0,rightEdge,lowEdge]},

        { type : 'TL', 'location' : [0,highEdge,leftEdge,1]},
        { type : 'TR', 'location' : [rightEdge,highEdge,1,1]},
        { type : 'BL', 'location' : [0,0,leftEdge,lowEdge]},
        { type : 'BR', 'location' : [rightEdge,0,1,lowEdge]}
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
        xMargin = 12./672.
        yMargin = 12./186.
        # virtual void SetMargin (Float_t left, Float_t right, Float_t bottom, Float_t top)
        if pad in [0,7]:
            gPad.SetMargin(xMargin,xMargin,yMargin,yMargin)
        elif pad in [1,2,3,4,5,6]:
            gPad.SetMargin(yMargin,yMargin,xMargin,xMargin)
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
        if plot['position'] == 'TT':
            histo = flipSummaryPlot(plot['plot'])
        elif plot['position'] != 'BB':
            histo = rotateSummaryPlot(plot['plot'])
        else:
            histo = plot['plot']
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
    palette.SetLabelSize(0.025)
#    palette.SetLabelFont(42)
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
