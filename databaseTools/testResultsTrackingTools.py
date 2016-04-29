#!/usr/bin/env python
import os,sys,string,urllib
import datetime as dt
import threading
import json

###############################################################################

# function that takes a list of modules as input and returns
# a dictionary containing grade for the most recent
# -20C test results in MoReWeb
# returns grade = None if no results found

def produceMoReWebGradeDictionary(modules):
    print "scraping MoReWeb Overview"
    moduleData = {}
    for module in modules:
      moduleData[module] = {}
      moduleData[module]["date_m20"] = None
      moduleData[module]["date_p17"] = None
      moduleData[module]["date_xray"] = None
      moduleData[module]["Moreweb Grade m20"] = None
      moduleData[module]["Moreweb Grade p17"] = None
      moduleData[module]["Moreweb Grade X-ray"] = None

    query = "http://www.physics.purdue.edu/cmsfpix/MoReWeb/Results/Overview.html"
    lines = []

    input = urllib.urlopen(query).readlines()
    for index, line in enumerate(input):
      for module in modules:
          if module not in line:
              continue

          if "m20_1" in input[index+13]:
              current_date = input[index+4].strip()
              if current_date > moduleData[module]["date_m20"]:
                  moduleData[module]["date_m20"] = input[index+4].strip()
                  moduleData[module]["Moreweb Grade m20"] = input[index+16].strip()

          elif "p17_1" in input[index+13]:
              current_date = input[index+4].strip()
              if current_date > moduleData[module]["date_p17"]:
                  moduleData[module]["date_p17"] = input[index+4].strip()
                  moduleData[module]["Moreweb Grade p17"] = input[index+16].strip()

          elif "XRayHRQualification" in input[index+13]:
              current_date = input[index+4].strip()
              if current_date > moduleData[module]["date_xray"]:
                  moduleData[module]["date_xray"] = input[index+4].strip()
                  moduleData[module]["Moreweb Grade X-ray"] = input[index+16].strip()


    for module, data in moduleData.iteritems():
        del data["date_m20"]
        del data["date_p17"]
        del data["date_xray"]
    return moduleData

###############################################################################

# function that takes a list of modules as input and returns
# a dictionary containing lessweb grade
# returns grade = None if no results found

def produceLesswebGradeDictionary(modules, force = False):

    with open('moduleGrades.json', 'r') as fp:
        gradeDictionary = json.load(fp)

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
        splitline = line.split("ROC")
        for chunk in splitline[1:]:
            flag = "Failure Mode: "
            if flag in chunk:
                roc = chunk[0]
                start = chunk.find(flag) + len(flag)
                end = chunk.find("<br>",start)
                moduleData[module]["ROC"+str(roc)+" Failure"] = chunk[start:end]

    return moduleData


###############################################################################

# function that takes a list of modules as input and returns
# a dictionary containing moreweb and lessweb grades
# returns grade = None if no results found

def produceGradeDictionary(modules, force):

    lesswebDictionary = produceLesswebGradeDictionary(modules, force)

    morewebDictionary = produceMoReWebGradeDictionary(modules)

    gradeDictionary = {}

    for module, data in morewebDictionary.iteritems():
        if module not in gradeDictionary:
            gradeDictionary[module] = {}
        gradeDictionary[module].update(data)

    for module, data in lesswebDictionary.iteritems():
        if module not in gradeDictionary:
            gradeDictionary[module] = {}
        gradeDictionary[module].update(data)

    return gradeDictionary


