#! /usr/bin/env python

from sys import argv
import os
import subprocess
import socket
from time import strftime
from config import *

testCenter='FNAL'

affirmativeResponses= ['true', 'True', '1', 't', 'T', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'most def']

try:
    test=argv[1]
    doCold=argv[2] in affirmativeResponses
    HighVoltage=argv[3] in affirmativeResponses
except:
    test=raw_input('\nEnter test name (Pretest, Fulltest, IV, FPIXTest, or FPIXROCTest)\n')
    doCold=raw_input('\nPerform test at -20C? (y/n)\n').strip() in affirmativeResponses
    HighVoltage=raw_input('\nPerform test at -300V? (y/n)\n').strip() in affirmativeResponses
    print '\n'

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

Tini=os.getenv('HOME')+'/elComandante/config/elComandante.ini.default'
Tconf=os.getenv('HOME')+'/elComandante/config/elComandante.conf.default'

testString={}
testString['Pretest']='Pretest@27'
testString['Fulltest']='Fulltest@T'
IVString = ""
for i in range(len(moduleNames)):
    if moduleNames[i] is not '0':
        IVString += 'IV_'+str(i)+'@T,'
IVString.rstrip(',')
testString['IV']=IVString
testString['FPIXTest']='FPIXTest@T,'+testString['IV']
testString['FPIXROCTest']='FPIXROCTest@T,'+testString['IV']

if doCold: temp='-20'
else:      temp='17'

if HighVoltage: biasvoltage='-300'
else:           biasvoltage='-150'

morewebTestString={}
morewebTestString['FPIXTest']='FPIXTest@T'.replace('@T','@'+temp+'C').replace('-','m').replace('@','-')
morewebTestString['FPIXROCTest']='FPIXROCTest@T'.replace('@T','@'+temp+'C').replace('-','m').replace('@','-')
morewebTestString['Pretest']='Pretest-27C'

############################################################
############################################################
############################################################

if test not in testString.keys():
    raise Exception('Not a valid test')

if len(moduleNames)==0 or len(moduleNames)>4:
    raise Exception('Too few or too many modules specified')

timeStamp=strftime('%y%m%d-%H%M')

replacements=[['TESTS',testString[test].replace('@T','@'+temp)],
              ['MOREWEBTESTNAME',morewebTestString[test]+'-'+testCenter+'-'+timeStamp+biasvoltage+'V'],
              ['BIASVOLTAGE',biasvoltage]]

replacements.append(['OPERATOR',shifter])
if test=="FPIXROCTest": replacements.append(['Full','Roc'])
for i in range(4):
    if moduleNames[i] is not '0':
        replacements.append(['USEM'+str(i),'True'])
        replacements.append(['MODULE'+str(i),moduleNames[i]])
    else:
        replacements.append(['USEM'+str(i),'False'])

#station=os.environ['HOME'].split('/')[2]
#replacements.append(['TESTCENTER',station])
replacements.append(['TESTCENTER',testCenter])

replacements.append(['HOSTNAME',socket.gethostname()])

ini=Tini.replace('.default','')
conf=Tconf.replace('.default','')

subprocess.call(['cp',Tini,ini])
subprocess.call(['cp',Tconf,conf])

for replacement in replacements:
    #print replacement
    subprocess.call(['sed','s/'+replacement[0]+'/'+replacement[1]+'/','--in-place',ini])
    subprocess.call(['sed','s/'+replacement[0]+'/'+replacement[1]+'/','--in-place',conf])

print '\npreparation complete\n'
