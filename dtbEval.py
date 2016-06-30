#!/usr/bin/env python
import sys
import os
import glob
import pandas as pd
import datetime
import math

from ROOT import TH1F, TH2F,TLegend, TCanvas, gROOT, gStyle

from ROOT import (kRed, kOrange, kYellow, kGreen,
                  kBlue, kViolet, kPink, kCyan, kBlack, kGray)

gROOT.SetBatch()
gStyle.SetOptStat(0)

colors = (10 * [kRed+1, kOrange+1, kYellow+1, kGreen+1,
          kBlue+1, kViolet+1, kPink+1, kCyan+1, kBlack, kGray])

inputDir = os.path.expanduser('~') + "/PlotsAndTables/UniqueTestResults/"

testDirs = []
for thing in os.listdir(inputDir):
    if os.path.isdir(inputDir+"/"+thing) and "M-" in thing:
        testDirs.append(inputDir+"/"+thing)


# build pandas dataframe with following columns
# DTB, test date, errors,
# then calculate columns
# isGoodTest, orderInDay

dictionary = {}
for index,dir in enumerate(testDirs):
    log_files = glob.glob(dir + "/*/commander*log")
    if not len(log_files):
        print "no log found for dir:", dir
        continue
    log_file = log_files[0]
    date = log_file.split("/")[-3].split("_")[-3]
    time = log_file.split("/")[-3].split("_")[-2]
    nErrors = 0
    with open(log_file) as data_file:
        for line in data_file:
            if "Board id:" in line:
                dtb = line.split()[-1]
            if "ERROR:" in line:
                nErrors +=1
    dictionary[index] = {'DTB':dtb,'Errors':nErrors,'Date':date,'Time':time}

df = pd.DataFrame.from_dict(dictionary, orient='index')

def isGoodTest(row):
    return row['Errors'] < 10
df['Is Good Test'] = df.apply(lambda row: isGoodTest(row), axis=1)

df['Order in Day'] = df.groupby(['Date','DTB'])['Time'].rank(ascending=True)

#####
# pull in historical weather data
#####
url = 'https://www.wunderground.com/history/airport/KDPA/2015/12/2/CustomHistory.html?dayend=20&monthend=6&yearend=2016&req_city=&req_state=&req_statename=&reqdb.zip=&reqdb.magic=&reqdb.wmo=&format=1'
weather = pd.read_csv(url,skipinitialspace=True)

def changeDateFormat(row):
    date_object = datetime.datetime.strptime(row['CDT'], '%Y-%m-%d')
    return date_object.strftime('%Y-%m-%d')
weather['Date'] = weather.apply(lambda row: changeDateFormat(row), axis=1)
weather = weather[['Date', 'Max TemperatureF','Mean Humidity']]
weather.rename(columns={'Max TemperatureF':'Max Temp'},inplace=True)
#####

frame = pd.merge(df,weather,on='Date',how='left')

#print frame.columns

#sys.exit(0)

#############################################

# now let's make some plots!!!

# things to check:
# -variation between DTBs X
# -variation over time X
# -variation with weather X
# -DTB heating up throughout day X


isGoodTest = frame['Is Good Test'].tolist()
dates = frame['Date'].tolist()
errors = frame['Errors'].tolist()


# 1D: number of errors per test (to motivate cut on # errors) DONE
maxErrors = 100
nErrorsPlot = TH1F("nErrors","number of errors per test", 100, 0, maxErrors)

# 1D: total failure fraction for each DTB integrated over time
dtbs = frame['DTB'].tolist()
dtbSet = frame['DTB'].unique().tolist()
nDTBs = len(dtbSet)

testsPerDTBPlot = TH1F("testsPerDTB","tests per DTB", nDTBs, 0, nDTBs)
testsPerDTBPlot.GetYaxis().SetTitle("number of tests")
testsPerDTBPlot.GetXaxis().SetTitle("DTB number")
for bin in range(nDTBs):
    testsPerDTBPlot.GetXaxis().SetBinLabel(bin+1,str(dtbSet[bin]))

failurePerDTBPlot = TH1F("failurePerDTB","failure rate per DTB", nDTBs, 0, nDTBs)
failurePerDTBPlot.GetYaxis().SetTitle("failure rate [%]")
failurePerDTBPlot.GetXaxis().SetTitle("DTB number")
for bin in range(nDTBs):
    failurePerDTBPlot.GetXaxis().SetBinLabel(bin+1,str(dtbSet[bin]))



# 1D: daily failure rate for each DTB as a function of date
dates = frame['Date'].tolist()
testsPerDayPlots = []
failureRatePerDayPlots = []
start_date = datetime.datetime.strptime('2015-12-02', '%Y-%m-%d')
end_date = datetime.datetime.strptime('2016-07-02', '%Y-%m-%d')
nDays = int(math.floor((end_date - start_date).days))
for index, dtb in enumerate(dtbSet):
    testsPlot = TH1F("testsPerDay_"+dtb,"tests per day", nDays, 0, nDays)
    testsPlot.GetYaxis().SetTitle("number of tests")
    testsPlot.GetXaxis().SetTitle("days since production began")
    testsPlot.SetLineColor(colors[index])
    testsPerDayPlots.append(testsPlot)

    failureRatePlot = TH1F("failurePerDay_"+dtb,"failure rate per day", nDays, 0, nDays)
    failureRatePlot.GetYaxis().SetTitle("failure rate [%]")
    failureRatePlot.GetXaxis().SetTitle("days since production began")
    failureRatePlot.SetLineColor(colors[index])
    failureRatePerDayPlots.append(failureRatePlot)

totalTestsPerDayPlot = TH1F("testsPerDay_total","tests per day", nDays, 0, nDays)
totalTestsPerDayPlot.GetYaxis().SetTitle("number of tests")
totalTestsPerDayPlot.GetXaxis().SetTitle("days since production began")
totalTestsPerDayPlot.SetLineColor(kBlack)

totalFailureRatePerDayPlot = TH1F("failurePerDay_total","failure rate per day", nDays, 0, nDays)
totalFailureRatePerDayPlot.GetYaxis().SetTitle("failure rate [%]")
totalFailureRatePerDayPlot.GetXaxis().SetTitle("days since production began")
totalFailureRatePerDayPlot.SetLineColor(kBlack)

# 2D: daily failure rate vs max temp
temps = frame['Max Temp'].tolist()

# 2D: daily failure rate vs max humidity
humidities = frame['Mean Humidity'].tolist()

# 1D: failure rates as a function of order in the day
orderInDay = frame['Order in Day'].tolist()


# loops over tests and fill histograms
###########################################################
nTests = len(frame.index)
for index in range(nTests):
    date = datetime.datetime.strptime(dates[index], '%Y-%m-%d')
    days = int(math.floor((date - start_date).days))
##########
    if errors[index] < maxErrors:
        nErrorsPlot.Fill(errors[index])
    else:
        nErrorsPlot.Fill(maxErrors - 0.1)
##########
    testsPerDTBPlot.Fill(dtbSet.index(dtbs[index]))
    if not isGoodTest[index]:
        failurePerDTBPlot.Fill(dtbSet.index(dtbs[index]))
##########
    testsPerDayPlots[dtbSet.index(dtbs[index])].Fill(days)
    if not isGoodTest[index]:
        failureRatePerDayPlots[dtbSet.index(dtbs[index])].Fill(days)



# normalize histograms, etc., draw and save canvases
###########################################################

##########
canvas1 = TCanvas()
canvas1.SetLogy()
nErrorsPlot.Draw()
canvas1.SaveAs("nErrors.pdf")
##########

##########
canvas2 = TCanvas()
failurePerDTBPlot.Divide(testsPerDTBPlot)
failurePerDTBPlot.Scale(100)
failurePerDTBPlot.SetMinimum(0)
failurePerDTBPlot.Draw()
canvas2.SaveAs("failurePerDTB.pdf")
##########

##########
canvas3 = TCanvas()
testsPerDTBPlot.SetMinimum(0)
testsPerDTBPlot.Draw()
canvas3.SaveAs("testsPerDTB.pdf")
##########

##########
canvas4 = TCanvas()
legend1 = TLegend(0.8, 0.6, 0.9, 0.9)
legend1.SetBorderSize(0)
legend1.SetFillStyle(0)
for index, plot in enumerate(testsPerDayPlots):
    totalTestsPerDayPlot.Add(plot)
    legend1.AddEntry(plot,"DTB " +dtbSet[index],"L")
legend1.AddEntry(totalTestsPerDayPlot,"total","L")
totalTestsPerDayPlot.Draw("same")
for plot in testsPerDayPlots:
    plot.Draw("same")
legend1.Draw()
canvas4.SaveAs("testsPerDay.pdf")
##########

##########
canvas5 = TCanvas()
legend2 = TLegend(0.8, 0.6, 0.9, 0.9)
legend2.SetBorderSize(0)
legend2.SetFillStyle(0)
for index, plot in enumerate(failureRatePerDayPlots):
    totalFailureRatePerDayPlot.Add(plot)
    plot.Divide(testsPerDayPlots[index])
    plot.Scale(100)
    legend2.AddEntry(plot,"DTB " +dtbSet[index],"L")
    plot.Draw("same")
totalFailureRatePerDayPlot.Divide(totalTestsPerDayPlot)
totalFailureRatePerDayPlot.Scale(100)
legend2.AddEntry(totalFailureRatePerDayPlot,"total","L")
totalFailureRatePerDayPlot.Draw("same")
legend2.Draw()
canvas5.SaveAs("failureRatePerDay.pdf")
##########
