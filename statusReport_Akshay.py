# Updated version of statusReport to allow multiple output lines to be
# overwritten using the curses module and to send emails and/or text messages
# about testing progress
#
# Akshay



# TODO: make way to detect hung test
# MAYBE: convert to multithreaded or multiprocessing to make quicker and better for detecting problems. May take up to many resources though.


import curses
import time
import sys
import os
from config import moduleNames, goodModuleNames
import glob
import smtplib
from optparse import OptionParser
import datetime


def failedTest(line):
	if "not programmable; stop" in line or\
	"Incomplete DAQ data readout" in line or\
	"empty results" in line or\
	"Abort data processing" in line or\
	"Event ID mismatch" in line:
		return True

#def hungTest(lines):
#	numAbortFlags = 0
#	numReadoutFlags = 0
#	
#	for i in lines:
#		if "CRITICAL" in i and "Abort data processing" in i:
#			numAbortFlags += 1
#		if "CRITICAL" in i and "Incomplete DAQ data readout" in i:
#			numReadoutFlags += 1

def sendEmail(receiver,content):
	s = smtplib.SMTP('smtp.mail.com',587)
        s.ehlo()
	s.starttls()
	s.login("cmsfpix@mail.com","PixelUpgrade")
	s.sendmail("cmsfpix@mail.com",[receiver],content)
	s.quit()


def sendText(phone,provider,content):
	
	att = ["@txt.att.net","a","A","att","ATT","atnt","ATNT","atat","ATAT","at&t","AT&T"]
	tmobile = ["@tmomail.net","t","T","tmo","Tmo","t-mo","T-mo","T-MO","t-mobile","T-mobile","T-Mobile"]
	verizon = ["@vtext.net","v","V","ver","Ver","verizon","Verizon"]
	sprint = ["@messaging.sprintpcs.com","s","S","sprint","Sprint"]
	uscellular = ["@email.uscc.net","us","US","usc","USC","uscellular","uscc","USCC"]
	
	networks = (att,tmobile,verizon,sprint,uscellular)
	to = ""
	for i in networks:
		if provider in i:
			to = str(phone)+i[0]

	s = smtplib.SMTP('smtp.mail.com',587)
        s.ehlo()
	s.starttls()
	s.login("cmsfpix@mail.com","PixelUpgrade")

	message = ("From: %s\r\n" % "cmsfpix@mail.com"
           + "To: %s\r\n" % to
           + "Subject: %s\r\n" % "Testing Progress"
           + "\r\n"
           + content)

	s.sendmail("cmsfpix@mail.com",to,message)
	s.quit()

"""
def getScurvesTime(scurve):
	#tries to estimate the time it takes for scurves to finish
	scurveStart = scurve[0].split()[0].replace('[','').replace(']','').split('.',1)[0]
	scurveDone = scurve[1].split()[0].replace('[','').replace(']','').split('.',1)[0]
	
	FMT = '%H:%M:%S'
	#tdelta = datetime.strptime(scurveDone, FMT) - datetime.strptime(scurveStart, FMT)
	tdelta = time.strptime(scurveDone, FMT) - time.strptime(scurveStart, FMT)
	
	duration = int(tdelta.total_seconds())
	
	return duration
	

def getTimingTimes(timing):
	#tries to estimate the time it takes for timing to finish
	timingStart = timing[0].split()[0].replace('[','').replace(']','').split('.',1)[0]
	timingDone = timing[1].split()[0].replace('[','').replace(']','').split('.',1)[0]

	FMT = '%H:%M:%S'
	#tdelta = datetime.strptime(timingDone, FMT) - datetime.strptime(timingStart, FMT)
	tdelta = time.strptime(timingDone, FMT) - time.strptime(timingStart, FMT)
	
	duration = int(tdelta.total_seconds())
	
	return duration


def getTimes(lines):
	#Method to get duration of each test in seconds
	line = []
	scurves = []
	timing = []
	for i in lines:
		if "doTest()" in i:
			line.append(i)
		if "Scurves::doTest()" in i:
			scurves.append(i)
		if "Scurves::scurves() done" in i:
			scurves.append(i)
		if "Timing::doTest()" in i:
			timing.append(i)
	lineDone = []
	for i in line:
		if "done" in i:
			lineDone.append(i)
	times = []
	for i in lineDone:
		try:
			duration = i.split()[i.split().index("duration:")+1]		
			test = i.split()[3]	
			times.append("{} {}".format(test,duration))
		except ValueError:
			continue
	#must separate scurve and timing duration as they are not saved in logfile
	if len(scurves) > 0:
		scurveTime = "Scurves {}".format(getScurvesTime(scurves))
		for i in times:
			if "Trim" in i:
				index = times.index(i) + 1
				times.insert(index,scurveTime)
	if len(timing) > 0:
		timingTime = "Timing {}".format(getTimingTimes(timing))
		for i in times:
			if "Pretest" in i:
				index = times.index(i) + 1
				times.insert(index,timingTime)
	return times
"""

def main(stdscr):
	global options

	refreshRate = 15
	if options.refresh:
		refeshRate = options.refresh

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
		
	tests = [""] * len(inputFiles)

	failedTestFlag = [False] * len(inputFiles)
	sentFailedTestFlag = [False] * len(inputFiles)

	sent1000ErrorsFlag = [False] * len(inputFiles)
	sent10000ErrorsFlag = [False] * len(inputFiles)
	
	while 1:
		stdscr.addstr(0,12,"TB:")
		stdscr.addstr(1,8,"Module:")
		stdscr.addstr(2,6,"# Errors:")
		stdscr.addstr(3,3,"# Criticals:")
		stdscr.addstr(4,4,"# Warnings:")
		stdscr.addstr(5,2,"Current test:")
		#stdscr.addstr(6,0,"Finished tests:")
		
		for j in range(len(inputFiles)):
			logFile = glob.glob(inputFiles[j] + '/' + "000*/commander_*.log")
			
			if logFile:
				with open(logFile[0]) as f:
					lines = f.readlines()

					currentTest = ""
					numCritical = 0
					numErrors = 0
					numWarning = 0
					#times = []
					for i in lines:
						if "doTest()" in i and "done" not in i:
							#times = getTimes(lines)
							currentTest = i.split(" ")[7].split("::")[0].replace("PixTest","")
							if currentTest == "Timing":
								if "Timings are not good" in i:
									if options.email:
										sendEmail(options.email,"Timings are not good")
								if options.text:
									sendText(options.text,options.provider,"Timings are not good")
									
									
						if "this is the end" in i:
							currentTest = "FPIXtest Done"
							IVTest = glob.glob(inputFiles[j] + '/' + "001*/IV.log")
							if IVTest:
								currentTest = "IV test"
								with open(IVTest[0]) as L:
									IVlines = L.readlines()
									for k in IVlines:
										if "this is the end" in k:
											currentTest = "ALL done"
						if "ERROR:" in i:
							numErrors += 1
						if "CRITICAL:" in i:
							numCritical += 1
						if "WARNING:" in i:
							numWarning += 1

						failedTestFlag[j] = failedTest(i)
						if failedTestFlag[j] == True and sentFailedTestFlag[j] == False:
								if options.email:
									sendEmail(options.email,"Module {} may have failed the {} test".format(j,currentTest))
									sentFailedTestFlag[j] = True
								if options.text:
									sendText(options.text,options.provider,"Module {} may have failed the {} test".format(j,currentTest))
									sentFailedTestFlag[j] = True

					tests[j] = currentTest
					if numErrors > 1000:
						if sent1000ErrorsFlag[j] == False:
							if options.email:
								sendEmail(options.email,"Module {} has exceeded 1000 errors".format(j))
								sent1000ErrorsFlag[j] = True
							if options.text:
								sendText(options.text,options.provider,"Module {} has exceeded 1000 errors".format(j))
								sent1000ErrorsFlag[j] = True
						else:
							pass
					if numErrors > 10000:
						if sent10000ErrorsFlag[j] == False:
							if options.email:
								sendEmail(options.email,"Module {} has exceeded 10000 errors".format(j))
								sent10000ErrorsFlag[j] = True
							if options.text:
								sendText(options.text,options.provider,"Module {} has exceeded 10000 errors".format(j))
								sent10000ErrorsFlag[j] = True
						else:
							pass

					stdscr.addstr(0,(j+1)*18,tbLine[j+1])
					stdscr.addstr(1,(j+1)*18,idLine[j+1])
					stdscr.addstr(2,(j+1)*18,"{}".format(numErrors))
					stdscr.addstr(3,(j+1)*18,"{}".format(numCritical))
					stdscr.addstr(4,(j+1)*18,"{}".format(numWarning))
					stdscr.addstr(5,(j+1)*18,currentTest)
					#for i in range(len(times)):
					#	stdscr.addstr(i+6,(j+1)*18,times[i])

		
		stdscr.refresh()
		time.sleep(refreshRate)
		stdscr.clear()
		
		isDone = all(t == "ALL done" for t in tests)
		if isDone == True:
			break
		
	if options.email:
		sendEmail(options.email,"Test is finished. Box is warming up")
	if options.text:
		sendText(options.text,options.provider,"Test is finished. Box is warming up")
	time.sleep(10)


parser = OptionParser()
parser.add_option("-e","--email",dest = "email",help = "receive alerts by email address")
parser.add_option("-t","--text",dest = "text",help = "receive alerts by text message")
parser.add_option("-r","--refresh",dest = "refresh",help = "time to refresh data output",type = int)
parser.add_option("-p","--provider",dest = "provider",help = "cell phone service provider")

(options, args) = parser.parse_args()

if options.text and not options.provider:
	print "\nneed to enter the network service provider to receive text message\n"
	exit()

if options.text:
	print "\n\n\nWARING:\tsome sms gateways may not work with the number and provider given\n\tReceiving text messages may incur charges if you do not have an unlimited messaging plan\n\tSome providers might require data to be turned on which might also incur charges\n"
	time.sleep(10)

curses.wrapper(main)
