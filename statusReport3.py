#!/usr/bin/env python
import sys
import os
import time
import glob
import smtplib
from config import moduleNames, goodModuleNames #,shifter ,shifterEmail
from datetime import datetime

tbLine = ["TB:"]
idLine = ["module ID:"]

inputDir = os.path.expanduser('~') + "/allTestResults/"

tbs = []
inputFiles = []
for index, module in enumerate(moduleNames):

    if module == "0":
        continue

    tbs.append(index)
    testDirs = glob.glob(inputDir + "/" + module + "_*")
    testDirs.sort(key=lambda x: os.path.getmtime(x))
    testDir = testDirs[-1]
    inputFiles.append(testDir)

for index, module in enumerate(goodModuleNames):
    tbLine.append(str(tbs[index]))
    idLine.append(module)

class bcolors:
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
def warningWrap(str):
    return bcolors.WARNING + str + bcolors.ENDC
def errorWrap(str):
    return bcolors.ERROR + str + bcolors.ENDC


def formatLine(output):
    # take output list & return formatted string
    columnWidth = 23 #15
    line = ""
    for entry in output:
        if '\033' in entry:
            line += " "*(columnWidth - len(str(entry)) + 9) + str(entry) + " "
        else:
            line += " "*(columnWidth - len(str(entry))) + str(entry) + " "
    return line

def moduleCrash(line):
    # following keywords suggest test failure
    isCrashed = False
    if "not programmable; stop" in line or\
        "Incomplete DAQ data readout" in line or\
        "empty results" in line or\
        "Abort data processing" in line or\
        "Event ID mismatch" in line:
        isCrashed = True
    return isCrashed

def checkEqual(list, str):
    # check if all elements in `list` equal to `str`,
    # blank elements are excluded.
    allEqual = True
    for element in list:
        if element == "":
            continue
        if element != str:
            allEqual = False
    return allEqual

def str2time(str):
    return datetime.strptime(str,'%H:%M:%S')

def endPrint():
    print '#'*130
    print '''\nFull test done!
    An email of summary has been sent to shifter with address provided.\n
    Please wait for a few minutes while results are processing and saving, 
    until you are prompt to hit `ENTER` on console.\n
    [statusReport] This is the end, my friEND.
    '''

def sendEmail(receiver, content):
    # Using mail.com because of easy registration
    s = smtplib.SMTP('smtp.mail.com', 587)
    s.starttls()
    s.login("cmsfpix@mail.com","PixelUpgrade")
    s.sendmail('cmsfpix@mail.com', [receiver], content)
    s.quit()

os.system('clear')
snapshot = ['']*7
snapshot[0] = formatLine(tbLine)
snapshot[1] = formatLine(idLine)

while 1:
    time.sleep(2)
    os.system("printf '\033c'") # clean screen
    idOutput = [e for e in idLine]
    testOutput = ["current test:"]
    timeOutput = ["time duration:"]
    errorOutput = ["# pXar errors:"]
    criticalOutput = ["# Criticals:"]
    warningOutput = ["# Warnings:"]
    testStartTime = ['']*4
    ivFirstEnterFlag = [1]*4
    ivEndTime = [0]*4
    ivDoneFlag = [0]*4
    for index, moduleDir in enumerate(inputFiles):
        test = ""
        timePassed = ""
        nErrors = 0
        nCriticals = 0
        nWarnings = 0
        fpixTestLog = glob.glob(moduleDir + '/' + "000*/commander_*.log")
        if fpixTestLog:
            with open(fpixTestLog[0]) as data_file:
                for line in data_file:
                    if line[0] != '[':
                        continue
		    if "ERROR:" in line:
                        nErrors += 1 
                    if "CRITICAL:" in line:
                        nCriticals += 1
                    if "WARNING:" in line:
                        nWarnings += 1
                    nowTime = datetime.now().time().strftime('%H:%M:%S') #line.split(" ")[0].strip('[]')[:-4]
                    if testStartTime[index]:
                        timePassed = str2time(nowTime) - str2time(testStartTime[index])
                    #if len(line.split(" ")) < 5:
                        #continue
                   # if len(line.split(" ")) > 10:
                    if "done" not in line and "took" not in line and "end" not in line:
                        if len(line.split(" ")) >10 and "::" in line.split(" ")[10] and "PixTest" in line.split(" ")[10]:
                            test = line.split(" ")[10].replace("PixTest","").replace("()","")
                        if "doTest()" in line:
                            test = line.split(" ")[7].replace("PixTest","").replace("()","")
                        #else:
                        #  continue
                        #if test[-1] == ',':
                        #    test = test[:-1]
                        testStartTime[index] = line.split(" ")[0].strip('[]')[:-4]
                        if test[-6:]=="doTest":
                            test = test.replace("::doTest","")
                    if moduleCrash(line):
                        test += "/Fail"
                    if "this is the end" in line:
                        ivTestLog = glob.glob(moduleDir + '/' + "001*/IV.log")
                        if ivTestLog:
                            test = "IVtest"
                            with open(ivTestLog[0]) as data_file1:
                                for line in data_file1:
				    if "Welcome" in line:
					testStartTime[index] = line.split(" ")[0].strip('[]')[:-4]
                                    if not ivDoneFlag[index]:
                                        nowTime = datetime.now().time().strftime('%H:%M:%S')
                                    else:
                                        nowTime = ivEndTime[index]
                                    timePassed = str2time(nowTime) - str2time(testStartTime[index])
                                    if "this is the end" in line:
                                        test = "ALL done"
                                        ivDoneFlag[index] = 1
                                        ivEndTime[index] = nowTime
                if nWarnings:
                    idLine[index+1] = warningWrap(idLine[index+1])
                if nErrors:
                    idOutput[index+1] = errorWrap(idLine[index+1])
        testOutput.append(test)
        timeOutput.append(str(timePassed))
        errorOutput.append(str(nErrors))
        criticalOutput.append(str(nCriticals))
        warningOutput.append(str(nWarnings))
    snapshot[1] = formatLine(idOutput)
    snapshot[2] = formatLine(testOutput)
    snapshot[3] = formatLine(timeOutput)
    snapshot[4] = formatLine(errorOutput)
    snapshot[5] = formatLine(criticalOutput)
    snapshot[6] = formatLine(warningOutput)
    for row in snapshot:
        print row
    #if checkEqual(testOutput[1:], "ALL done"):
        #content = "Hello " + shifter\
        #        + ",\n\nYour module tests are finished, summarized as bellow:\n\n"\
        #        + '\t' + snapshot[0] + '\n'\
        #        + '\t' + snapshot[1] + '\n'\
        #        + '\t' + snapshot[4] + '\n'\
        #        + '\t' + snapshot[5] + '\n'\
        #        + '\t' + snapshot[6] + '\n'\
        #        + "\n\nThank you!"
        #sendEmail(shifterEmail, content) #shifterEmail imported from config
       # endPrint()
       # break
