#!/Usr/bin/env python
import os,sys#,string,urllib2

from moduleTrackingTools import *
from componentTrackingTools import *

import pandas as pd
import json

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--file", dest="inputFileName",
                  help="path to input file containing a list of modules, one per line")
(arguments, args) = parser.parse_args()

from ROOT import gROOT, TH2F, TCanvas, gStyle

gROOT.SetBatch()

if arguments.inputFileName:
    modules = [line.rstrip('\n') for line in open(arguments.inputFileName)]
else:
    partsDictionary = producePartsDictionary()
    modules = [module for module in partsDictionary.index.tolist()]

if not os.path.exists('moduleInfo.json'):
    print "please run 'updateModuleDB.py' to produce module grade dictionary"
    sys.exit(0)

with open('moduleInfo.json') as json_data:
    gradeDictionary = json.load(json_data)

df = pd.DataFrame.from_dict(gradeDictionary, orient='index')
df = df[['Grade','Moreweb Grade m20','Moreweb Grade p17']]

def getMorewebGrade(row):
    if not pd.isnull(row['Moreweb Grade m20']):
        return row['Moreweb Grade m20']
    elif not pd.isnull(row['Moreweb Grade p17']):
        return row['Moreweb Grade p17']
    else:
        return 'I'

df['Moreweb Grade'] = df.apply(lambda row: getMorewebGrade(row), axis=1)
df.rename(columns = {'Grade' : 'Lessweb Grade'}, inplace=True)

df = df[['Lessweb Grade','Moreweb Grade']]
df.fillna(value='I',inplace=True)

dictionary = df.to_dict(orient='index')

gradePlot = TH2F("Module Grade Comparison",";lessweb;MoReWeb",4,0,4,4,0,4)
gradePlot.SetStats(False)
labels = ["A", "B", "C", "I"]
for bin in range(len(labels)):
    gradePlot.GetXaxis().SetBinLabel(bin+1,str(labels[bin]))
    gradePlot.GetYaxis().SetBinLabel(bin+1,str(labels[bin]))




nModules = 0
for module in modules:
    if module not in dictionary:
        print module, "missing from grade dictionary"
        continue
    nModules += 1
    data = dictionary[module]
    # change NaN to "I"
    for entry in data:
        if pd.isnull(data[entry]):
            data[entry] = "I"
    gradePlot.Fill(labels.index(data["Lessweb Grade"]), labels.index(data["Moreweb Grade"]))

canvas = TCanvas()

gStyle.SetTextFont(42)
gradePlot.SetMarkerSize(3)
gradePlot.Draw("colz text")
canvas.SetMargin(0.11,0.11,0.15,0.1)
gradePlot.SetTitle("Module Grade Comparison (" + str(nModules) + " modules)")
gradePlot.GetXaxis().SetLabelSize(0.1)
gradePlot.GetXaxis().SetLabelSize(0.1)
gradePlot.GetYaxis().SetLabelSize(0.1)
gradePlot.GetXaxis().SetTitleSize(0.08)
gradePlot.GetYaxis().SetTitleSize(0.08)
gradePlot.GetXaxis().SetTitleOffset(0.8)
gradePlot.GetYaxis().SetTitleOffset(0.6)
gradePlot.GetXaxis().CenterTitle()
gradePlot.GetYaxis().CenterTitle()


canvas.SaveAs("ModuleGrades.pdf")



# export mismatched lines

df = df[(df['Lessweb Grade'] != df['Moreweb Grade']) & (df['Lessweb Grade'] != 'I')]
df.to_csv('MismatchedModuleGrades.csv', index_label = "Module")

