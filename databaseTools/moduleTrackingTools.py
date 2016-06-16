#!/usr/bin/env python
import os,sys,string
import requests
import datetime as dt
import threading
import json
import sys
import pandas as pd
from socket import error as SocketError

import csv
import urllib2
import numpy as np


###############################################################################

# function that returns a dictionary containing
# date and grade for the most recent
# test results in MoReWeb
# returns grade = None if no results found

def scrapeMoReWeb():
    print "scraping MoReWeb Overview"
    query = "http://inky.physics.purdue.edu/cmsfpix//MoReWeb/Results/Overview.html"
    dfs = pd.read_html(query, parse_dates=True)
    df = dfs[0]
    # get rid of special characters in column headings
    df.rename(columns=lambda col: col.replace('\t','').replace('\n',''), inplace=True)
    # choose relevant columns
    df = df[['Module ID','Test Date','Qualification Type','Test Type','Grade']]
#    # delete entries from non-official tests
#    df = df[(~df['Qualification Type'].str.contains('Purdue')) & (~df['Qualification Type'].str.contains('Quick'))]
    df = df[~df['Qualification Type'].str.contains('Quick')]

    # initialize output dictionary
    moduleData = {}
    modules = df['Module ID'].unique().tolist()
    for module in modules:
        moduleData[module] = {}
        moduleData[module]["Test Date m20"] = np.nan
        moduleData[module]["Test Date p17"] = np.nan
        moduleData[module]["Test Date xray"] = np.nan
        moduleData[module]["Moreweb Grade m20"] = np.nan
        moduleData[module]["Moreweb Grade p17"] = np.nan
        moduleData[module]["Moreweb Grade xray"] = np.nan

    # group data by module and test type, grab the most recent one
    grouped = df.groupby(['Module ID','Test Type'])
    for name, group in grouped:
        # sort by test date, grab most recent one
        sorted = group.sort_values('Test Date', ascending=False)
        test = sorted.iloc[0]
        module = test['Module ID']
        type = test['Test Type']
        date = test['Test Date']
        grade = test['Grade']

        if 'm20' in type:
            moduleData[module]["Test Date m20"] = date
            moduleData[module]["Moreweb Grade m20"] = grade
        elif 'p17' in type:
            moduleData[module]["Test Date p17"] = date
            moduleData[module]["Moreweb Grade p17"] = grade
        elif 'XRay' in type:
            moduleData[module]["Test Date xray"] = date
            moduleData[module]["Moreweb Grade xray"] = grade

    # convert to pandas dataframe and return
    df = pd.DataFrame.from_dict(moduleData, orient='index')
    return df

###############################################################################

# function to build a pandas dataframe from a "module report" CSV input
# use module name as key to dictionary

def produceModuleDictionary():

    url = 'http://inky.physics.purdue.edu/cmsfpix//Submission_p/tmp/modulereport2.csv'
    df = pd.read_csv(url, index_col="Module", skipinitialspace=True)

    # delete final empty column                                                                                                                                                                            
    df.drop(df.columns[[-1]], axis=1, inplace=True)

    # rename ROC failure mode columns
    for roc in range(16):
        df.rename(columns={'ROC'+str(roc): 'ROC'+str(roc)+' Failure'}, inplace=True)

    return df

###############################################################################

# function that takes a list of modules as input and returns
# a dictionary containing lessweb grade
# returns grade = None if no results found
# DEPRECATED

def scrapeLesswebFullTestSummary(modules, force = False):

    if os.path.exists('moduleGrades.json'):
        with open('moduleGrades.json', 'r') as fp:
            gradeDictionary = json.load(fp)
    else:
        gradeDictionary = {}

    modulesToProcess = []
    for module in modules:
        if force:
            modulesToProcess.append(module)
        elif module not in gradeDictionary:
            modulesToProcess.append(module)

    print "scraping PU DB full test summary pages, estimated time " + str(round(len(modulesToProcess)/120.,1)) + " minutes"
    moduleData = {}
    target = 0


    for index, module in enumerate(modulesToProcess):
        if index/float(len(modulesToProcess)) >= target/100.:
            sys.stdout.write(str(target) + "%")
            sys.stdout.flush()
            target += 10
        sys.stdout.write(".")
        sys.stdout.flush()

        if index == len(modulesToProcess) - 1:
            print

        moduleData[module] = {}
        moduleData[module]["Lessweb Grade"] = None

        query = "http://www.physics.purdue.edu/cmsfpix/Submission_p/summary/summaryFull.php?name=%s"%module

        lines = []

        # get url and skip first 9 lines
        url_ = urllib.urlopen(query)
        for index in range(10):
            url_.readline()

        # just read the beginning of the (very long) 10th line
        line = url_.read(2000)
        grade = line[line.find("Grade")+7]
        moduleData[module]["Lessweb Grade"] = grade

        # also parse ROC failure modes
        for roc in range(16):
            moduleData[module]["ROC"+str(roc)+" Failure"] = None
        if "ROC failure modes:" not in line:
            continue
        failureModeSection = line.split("ROC failure modes:")[1]
        splitline = failureModeSection.split("ROC")
        for chunk in splitline[1:]:
            splitChunk = chunk.split(":")
            roc = splitChunk[0]
            end = chunk.find("<br>")-len("<br>")
            moduleData[module]["ROC"+str(roc)+" Failure"] = splitChunk[1].strip()[:end].strip()
            # last ROC with a failure mode
            if "Timeable" in chunk:
                break

    return moduleData


###############################################################################

# function that takes a list of modules as input and returns
# a dictionary containing relevant dates of assembly/testing
# returns None if no results found
# DEPRECATED

def scrapeLesswebPartSummary(modules, force = False):

    if os.path.exists('moduleGrades.json'):
        with open('moduleGrades.json', 'r') as fp:
            gradeDictionary = json.load(fp)
    else:
        gradeDictionary = {}

    modulesToProcess = []
    for module in modules:
        if force:
            modulesToProcess.append(module)
        elif module not in gradeDictionary:
            modulesToProcess.append(module)

    print "scraping PU DB part summary pages, estimated time " + str(round(len(modulesToProcess)/120.,1)) + " minutes"
    moduleData = {}
    target = 0

    for index, module in enumerate(modulesToProcess):
        if index/float(len(modulesToProcess)) >= target/100.:
            sys.stdout.write(str(target) + "%")
            sys.stdout.flush()
            target += 10
        sys.stdout.write(".")
        sys.stdout.flush()

        if index == len(modulesToProcess) - 1:
            print

        moduleData[module] = {}
        moduleData[module]["Received Date"] = None
        moduleData[module]["Shipped Date"] = None
        moduleData[module]["Judgement Date"] = None

        query = "http://www.physics.purdue.edu/cmsfpix/Submission_p/summary/bbm.php?name=%s"%module

        lines = []

        try:
            r = requests.get(query)
        except:
            print "FAIL!!!!!!!!!!"

        if not r:
            continue
        for line in r.iter_lines():
            if "Received" in line:
                splitline = line.split("<br>")
                for chunk in splitline:
                    if "Received" in chunk:
                        moduleData[module]["Received Date"] = ' '.join(chunk.split()[:2])[:-3]
                        break
            if "Shipped" in line:
                moduleData[module]["Shipped Date"] = ' '.join(line.split()[:2])[:-3]
            if ("Ready for Mounting" in line or "Rejected" in line) and "Status" not in line:
                moduleData[module]["Judgement Date"] = ' '.join(line.split()[:2])[:-3]


    return moduleData

