#!/usr/bin/env python
import os,sys,string,urllib
import datetime as dt
import threading

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
      moduleData[module]["date"] = None
      moduleData[module]["moreweb grade"] = None

    query = "http://www.physics.purdue.edu/cmsfpix/MoReWeb/Results/Overview.html"
    lines = []

    input = urllib.urlopen(query).readlines()
    for index, line in enumerate(input):
      for module in modules:
        if module in line and "m20_1" in input[index+13]:
          current_date = input[index+4].strip()
          if current_date > moduleData[module]["date"]:
            moduleData[module]["date"] = input[index+4].strip()
            moduleData[module]["moreweb grade"] = input[index+16].strip()

    for module, data in moduleData.iteritems():
        del data["date"]
    return moduleData

###############################################################################

# function that takes a list of modules as input and returns
# a dictionary containing lessweb grade
# returns grade = None if no results found

def produceLesswebGradeDictionary(modules):
    print "scraping PU DB full test summary pages, estimated time " + str(round(len(modules)/120.,1)) + " minutes"
    moduleData = {}
    target = 0
    
    for index, module in enumerate(modules):
        if index/float(len(modules)) >= target/100.:
            sys.stdout.write(str(target) + "%")
            sys.stdout.flush()
            target += 10
        sys.stdout.write(".")
        sys.stdout.flush()

        if index == len(modules) - 1:
            print

        moduleData[module] = {}
        moduleData[module]["lessweb grade"] = None
        
        query = "http://www.physics.purdue.edu/cmsfpix/Submission_p/summary/summaryFull.php?name=%s"%module
        
        lines = []
        
        # get url and skip first 9 lines
        url_ = urllib.urlopen(query)
        for index in range(10):
            url_.readline()

        # just read the beginning of the (very long) 10th line
        line = url_.read(500)
        grade = line[line.find("Grade")+7]
        moduleData[module]["lessweb grade"] = grade

    return moduleData


###############################################################################

# function that takes a list of modules as input and returns
# a dictionary containing moreweb and lessweb grades
# returns grade = None if no results found

def produceGradeDictionary(modules):

    lesswebDictionary = produceLesswebGradeDictionary(modules)

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


