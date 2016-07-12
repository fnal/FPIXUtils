# Updated version of statusReport to allow multiple output lines to be
# overwritten using the curses module.
#
# Akshay


# TODO: make a check for failed test
# TODO: make email or sms alert of finished test

import curses
import time
import sys
import os
from config import moduleNames, goodModuleNames
import glob


"""
def sendEmail(receiver,content):
	s = smtplib.SMTP('smtp.mail.com',587)
	s.starttls()
	s.login("cmsfpix@mail.com","PixelUpgrade")
	s.sendmail("cmsfpix@mail.com",[receiver],content)
	s.quit()
"""

def main(stdscr):
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
		
		
	

	
	inProgress = True	
	
	tests = [""] * len(inputFiles)
	
	while inProgress:
		stdscr.addstr(0,0,"TB:")
		stdscr.addstr(1,0,"Module:")
		stdscr.addstr(2,0,"Test:")
		stdscr.addstr(3,0,"# Errors:")
		stdscr.addstr(4,0,"# Criticals:")
		stdscr.addstr(5,0,"# Warnings:")

		for j in range(len(inputFiles)):
			logFile = glob.glob(inputFiles[j] + '/' + "000*/commander_*.log")
			
			if logFile:
				with open(logFile[0]) as f:
					lines = f.readlines()

					currentTest = ""
					numCritical = 0
					numErrors = 0
					numWarning = 0
					for i in lines:
						if "doTest()" in i and "done" not in i:
							currentTest = i.split(" ")[7].split("::")[0].replace("PixTest","")
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

					tests[j] = currentTest


					stdscr.addstr(0,(j+1)*18,tbLine[j+1])
					stdscr.addstr(1,(j+1)*18,idLine[j+1])
					stdscr.addstr(2,(j+1)*18,currentTest)
					stdscr.addstr(3,(j+1)*18,"{}".format(numErrors))
					stdscr.addstr(4,(j+1)*18,"{}".format(numCritical))
					stdscr.addstr(5,(j+1)*18,"{}".format(numWarning))

		
		stdscr.refresh()
		time.sleep(15)
		stdscr.clear()
		
		isDone = all(t == "ALL done" for t in tests)
		if isDone == True:
			break
		



curses.wrapper(main)
