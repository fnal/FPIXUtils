#! /usr/bin/env python
import os
import re
import sys

print '\n'
shifter=raw_input('Enter your name:\n')

moduleNames=[]
for i in range(4):
    print '\n'
    moduleName=raw_input('Enter module '+str(i)+' (starting from rear of coldbox) name, or press enter for no module:\n')
    moduleName=moduleName.upper()
    if moduleName:
        r = re.compile('[A-Z]-[A-Z]-[A-Z0-9]-[A-Z0-9][A-Z0-9]')
        s = re.compile('[A-Z]-[0-9][0-9]-[BT][RL]')
        if r.match(moduleName) is not None or s.match(moduleName) is not None:
            moduleNames.append(moduleName)
        else: 
            print 'Incorrect module name format. Aborting'
            sys.exit()
    else: moduleNames.append('0')

f=open(os.environ['HOME']+'/FPIXUtils/config.py','w')
f.write('shifter="'+shifter+'"\n\n')

f.write('moduleNames=[\n')
for i in range(0,len(moduleNames)):
    f.write('\t"'+moduleNames[i]+'",\n')
f.write(']\n\n')

f.write('goodModuleNames=[\n')
for i in range(0,len(moduleNames)):
    if moduleNames[i] is not '0':
        f.write('\t"'+moduleNames[i]+'",\n')
f.write(']')

f.close()

print '\nConfig file created\n'
