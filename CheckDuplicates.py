#!/usr/bin/env python
import argparse
import os

parser = argparse.ArgumentParser(description='Search through the production test directory and locate duplicate results and have user select which ones to move')
parser.add_argument('-d','--directory', dest='directory', default='.', help='Input directory to seach for duplicates')
parser.add_argument('-f','--filter', dest='filter', default='M-[A-Z]-[0-9A-Z]-[0-9A-Z][A-Z0-9]*/', help='ls filter used to find directories: M-[A-Z]-[0-9]-[0-9][0-9]*/')
parser.add_argument('--dryrun', dest='dryrun', action='store_true', default=False, help='Do not actually move directorys')
parser.add_argument('-t','--temperatures', dest='temperatures', nargs='+', default=['m20','17'], help='Temperatures to check')
args = parser.parse_args()

def handleduplicates(testlist):
    for index in range(len(testlist)): print str(index)+': '+testlist[index]
    if not args.dryrun:
        duplicates = raw_input('Enter the number(s) of the test results that should NOT be used:').split()
        if duplicates==[]: return
        for duplicate in duplicates: os.system('/bin/mv -v '+args.directory+"/"+testlist[int(duplicate)]+' Duplicates/')

resultlist = os.popen('/bin/ls -d '+args.directory+'/'+args.filter).readlines()
for iresult in range(len(resultlist)):
    result = resultlist[iresult]
    newresult = result[result.find("M-"):result.rfind("/")]
    resultlist[iresult] = newresult

modulelist = []
for result in resultlist: modulelist.append(result[result.find('M'):result.find('_')])
modules = set(modulelist)

for module in modules:
    duplicate = False
    resultsfound = []
    tempcounters = []
    for temp in args.temperatures:
        tempcounter = 0
        for result in resultlist:
            if result.find(module) != -1 and result.find('-'+temp+'C-') != -1:
                tempcounter += 1
                resultsfound.append(result)
        if tempcounter > 1: duplicate = True
        tempcounters.append(tempcounter)
    if duplicate:
        print str(max(tempcounters))+' Duplicates results found for module '+module
        handleduplicates(resultsfound)
