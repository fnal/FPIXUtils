###################################################################################################
#
#	Written by Trevor Scheopner 06/09/16
#	Purpose: Grab config files from Nebraska for new modules
#		and get those files ready for testing at KU
#	Usage: Run in the /home/CMS_pixel/Testing/pxar_fermi/ Directory using the command:
#		python2.6 ../FPIXUtils/grabUNLdataKU.py <moduleName>
#		If the module is named M-I-1-08 for example, <moduleName> = mi108
#
###################################################################################################


from glob import glob
import os
import subprocess
import sys
import string

modName = sys.argv[1]
dataName = modName+"data"
upperName = string.upper(modName)
formalName = upperName[0]+"-"+upperName[1]+"-"+upperName[2]+"-"+upperName[3]+upperName[4]

os.system("mkdir ./data/"+modName)
os.system("mkdir ./data/"+dataName)
os.chdir("/home/CMS_pixel/Testing/unl-ku-moduletesting/")
os.system("git pull origin master")
os.system("cp -r ./"+formalName+"_FPIXTest"+"* /home/CMS_pixel/Testing/pxar_fermi/data/"+modName)
os.chdir("/home/CMS_pixel/Testing/pxar_fermi/data/"+modName)
os.system("mv ./"+formalName+"_FPIXTest"+"* ./"+formalName)
os.system("cp ./"+formalName+"/000_FPIXTest_p17/* ./")
os.system("mv ./configParameters.dat ./configParametersOld.dat")

fOld = open("configParametersOld.dat", "r+")
f = open("configParameters.dat", "w")
lines = fOld.readlines()
fOld.close()
lines[0] = "testboardName *\n"

for line in lines:
	f.write(line)

f.close();

fDaq = open("testParameters.dat", "a")
fDaq.write("\n-- DAQ\ndelayTBM            checkbox\nfilltree            checkbox\ntrgfrequency(khz)   100\nmaskHotPixels       button\ntrgnumber           5\niterations          10\nrundaqtrg           button\ndaqseconds          5\nrundaqseconds       button")
fDaq.close

os.chdir("/home/CMS_pixel/Testing/pxar_fermi/")
