# Updated version of statusReport to allow multiple output lines to be
# overwritten using the curses module and to send emails and/or text messages
# about testing progress
#
# Akshay

# UPDATE: able to send emails and text messages (not tested on all providers yet)
# UPDATE: added  methods to get duration of completed tests
# UPDATE: commented out methods to get duration as it is not necessarily important
# UPDATE: added functionality to get number of errors per test
# UPDATE: added line of output that gets the runtime of each test
# UPDATE: window now resizes automatically based on number of modules being tested

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
from datetime import datetime

def str2time(string):
	return datetime.strptime(string,'%H:%M:%S')

def failedTest(line):
	if "not programmable; stop" in line or\
	"Incomplete DAQ data readout" in line or\
	"empty results" in line or\
	"Abort data processing" in line or\
	"Event ID mismatch" in line:
		return True


def hungTest(lines):
	numAbortFlags = 0
	numReadoutFlags = 0
	numFlawedEventFlag = 0
	numIdMismatchFlag = 0
	numDataSizeFlag = 0

	for i in lines:
		if "Abort data processing" in i:
			numAbortFlags += 1
		if "Incomplete DAQ data readout" in i:
			numReadoutFlags += 1
		if "Dumping the flawed event" in i:
			numFlawedEventFlag += 1
		if "Event ID mismatch" in i:
			numIdMismatchFlag += 1
		if "Data size does not correspond" in i:
			numDataSizeFlag += 1
		if "no scurve result histograms received" in i:
			return False


def sendEmail(receiver,content,numAttempts = 0):
	s = smtplib.SMTP('smtp.mail.com',587)
        s.ehlo()
	s.starttls()
	s.login("cmsfpix@mail.com","PixelUpgrade")
	try:
		s.sendmail("cmsfpix@mail.com",[receiver],content)
	except smtplib.SMTPRecipientsRefused:
		if numAttempts < 3:
			sendEmail(receiver,content,numAttempts+1)
		else:
			pass
	s.quit()

def sendText(phone,provider,content,numAttempts = 0):
	
	att = ["@txt.att.net","a","A","att","ATT","atnt","ATNT","atat","ATAT","at&t","AT&T"]
	tmobile = ["@tmomail.net","t","T","tmo","Tmo","t-mo","T-mo","T-MO","t-mobile","T-mobile","T-Mobile"]
	verizon = ["@vtext.net","v","V","ver","Ver","verizon","Verizon"]
	sprint = ["@messaging.sprintpcs.com","s","S","sprint","Sprint"]
	#uscellular = ["@email.uscc.net","us","US","usc","USC","uscellular","uscc","USCC"]
	
	networks = (att,tmobile,verizon,sprint)
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
	
	try:
		s.sendmail("cmsfpix@mail.com",to,message)
	except smtplib.SMTPRecipientsRefused:
		if numAttempts < 3:
			sendText(phone,provider,content,numAttempts+1)
		else:
			pass
	s.quit()

def getScurvesTime(scurve):
	#tries to estimate the time it takes for scurves to finish
	scurveStart = scurve[0].split()[0].replace('[','').replace(']','').split('.',1)[0]
	scurveDone = scurve[1].split()[0].replace('[','').replace(']','').split('.',1)[0]
	FMT = '%H:%M:%S'
	tdelta = datetime.strptime(scurveDone, FMT) - datetime.strptime(scurveStart, FMT)
	duration = int(tdelta.total_seconds())
	
	return duration

def getTimingTimes(timing):
	#tries to estimate the time it takes for timing to finish
	timingStart = timing[0].split()[0].replace('[','').replace(']','').split('.',1)[0]
	timingDone = timing[1].split()[0].replace('[','').replace(']','').split('.',1)[0]

	FMT = '%H:%M:%S'
	tdelta = datetime.strptime(timingDone, FMT) - datetime.strptime(timingStart, FMT)
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
			test = i.split()[3].replace("PixTest","").replace("::doTest()","")	
			times.append([test,duration])
		except ValueError:
			continue
	#must separate scurve and timing duration as they are not saved in logfile
	if len(scurves) > 1:
		scurveTime = ["Scurves",getScurvesTime(scurves)]
		for i in times:
			if "Trim" in i:
				index = times.index(i) + 1
				times.insert(index,scurveTime)
	if len(timing) > 1:
		timingTime = ["Timing",getTimingTimes(timing)]
		for i in times:
			if "Alive" in i:
				index = times.index(i) + 1
				times.insert(index,timingTime)
	return times

def errorByTest(lines):
	tests = []
	testOrder = []
	numERROR = 0
	currentTest = ""
	previousTest = ""
	for i in lines:
		if "doTest()" in i and not "done" in i:
			currentTest = i.split()[3].replace("PixTest","").replace("::doTest()","")
			testOrder.append(currentTest)
			try:
				previousTest = testOrder[len(testOrder)-2]
			except:
				continue
			tests.append([previousTest,numERROR])
			numERROR = 0
		if "ERROR:" in i:
			numERROR += 1
	
	tests.append([currentTest,numERROR])
	if "FPIXTest" in tests[0]:
		del tests[0]

	return tests	

def main(stdscr):
	global options

	refreshRate = 15
	if options.refresh:
		refreshRate = options.refresh

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

	#resize window to fit all output
	width = 24 * len(inputFiles)
	print "\x1b[8;20;" + str(width) + "t"

	tests = [""] * len(inputFiles)
	failedTestFlag = [False] * len(inputFiles)
	sentFailedTestFlag = [False] * len(inputFiles)
	sent1000ErrorsFlag = [False] * len(inputFiles)
	sent10000ErrorsFlag = [False] * len(inputFiles)
	currentTestDuration = []
	testStartTime = [""] * len(inputFiles)

	while 1:
		stdscr.clear()
		curses.start_color()
		curses.init_pair(1,curses.COLOR_WHITE,curses.COLOR_BLACK)
		curses.init_pair(2,curses.COLOR_RED,curses.COLOR_BLACK)
		curses.init_pair(3,curses.COLOR_GREEN,curses.COLOR_BLACK)

		stdscr.addstr(0,12,"TB:",)
		stdscr.addstr(1,8,"Module:")
		stdscr.addstr(2,6,"# Errors:")
		stdscr.addstr(3,3,"# Criticals:")
		stdscr.addstr(4,4,"# Warnings:")
		stdscr.addstr(5,2,"Current test:")
		stdscr.addstr(6,2,"test runtime:")
		stdscr.addstr(8,0,"Finished tests:")
		#stdscr.addstr(8,0,"(duration|Errors)")
		stdscr.addstr(9,4,"(# Errors)")
		
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
							
							#get the starting time of the test to see how long the test has been running
							testStartTime[j] = i.split(" ")[0].strip('[]')[:-4]

							if currentTest == "Timing":
								if "Timings are not good" in i:
									if options.email:
										sendEmail(options.email,"Timings are not good in module {}".format(idLine[j]))
								if options.text:
									sendText(options.text,options.provider,"Timings are not good in module {}".format(idLine[j]))
									
									
						if "this is the end" in i:
							currentTest = "FPIXtest Done"
							IVTest = glob.glob(inputFiles[j] + '/' + "001*/IV.log")
							if IVTest:
								currentTest = "IV test"
								testStartTime[j] = i.split(" ")[0].strip('[]')[:-4]
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
									sendEmail(options.email,"Module {} may be experiencing problems in the {} test".format(idLine[j],currentTest))
									sentFailedTestFlag[j] = True
								if options.text:
									sendText(options.text,options.provider,"Module {} may be experiencing problems in the {} test".format(j,currentTest))
									sentFailedTestFlag[j] = True

					tests[j] = currentTest
					prevErrors = errorByTest(lines)
					
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
					
					nowTime = datetime.now().time().strftime('%H:%M:%S')
					timePassed = str2time(nowTime) - str2time(testStartTime[j])
					if tests[j] == "FPIXtest Done" or tests[j] == "ALL done":
						timePassed = "-:--:--"

					stdscr.addstr(0,(j+1)*24-6,tbLine[j+1])
					stdscr.addstr(1,(j+1)*24-6,idLine[j+1])
					if numErrors > 0:
						stdscr.addstr(2,(j+1)*24-6,"{}".format(numErrors),curses.color_pair(2))
					else:
						stdscr.addstr(2,(j+1)*24-6,"{}".format(numErrors),curses.color_pair(1))

					if numCritical > 0:
						stdscr.addstr(3,(j+1)*24-6,"{}".format(numCritical),curses.color_pair(2))
					else:
						stdscr.addstr(3,(j+1)*24-6,"{}".format(numCritical),curses.color_pair(1))

					if numWarning > 0:
						stdscr.addstr(4,(j+1)*24-6,"{}".format(numWarning),curses.color_pair(2))
					else:
						stdscr.addstr(4,(j+1)*24-6,"{}".format(numWarning),curses.color_pair(1))
					stdscr.addstr(5,(j+1)*24-6,currentTest)
					
					stdscr.addstr(6,(j+1)*24-6,str(timePassed))

					for i in range(len(prevErrors)):
						if prevErrors[i][1] > 0:
							stdscr.addstr(i+8,(j+1)*24-6,"{} ({})".format(prevErrors[i][0],prevErrors[i][1]),curses.color_pair(2))
						else:
							stdscr.addstr(i+8,(j+1)*24-6,"{} ({})".format(prevErrors[i][0],prevErrors[i][1]),curses.color_pair(1))
						#if i < len(times):
						#	#stdscr.addstr(i+7,(j+1)*24+1+len(prevErrors[i][0]),"({}|{})".format(times[i][1],prevErrors[i][1]))
						#else:
						#	stdscr.addstr(i+7,(j+1)*24+1+len(prevErrors[i][0]),"({}|{})".format("IP",prevErrors[i][1]))
					
		
		stdscr.refresh()
		time.sleep(refreshRate)
		
		isDone = all(t == "ALL done" for t in tests)
		if isDone == True:
			if options.email:
				sendEmail(options.email,"Test is finished. Box is warming up")
			if options.text:
				sendText(options.text,options.provider,"Test is finished. Box is warming up")
			time.sleep(30)
			return
		



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
	print "\x1b[8;20;100t"
	print "\n\n\nWARING:\tsome sms gateways may not work with the number and provider given\n\tReceiving text messages may incur charges if you do not have an unlimited messaging plan\n\tSome providers might require data to be turned on which might also incur charges\n"
	time.sleep(10)

curses.wrapper(main)
