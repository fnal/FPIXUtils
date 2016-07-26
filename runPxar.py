from glob import glob
import os
import subprocess
import sys
import string

fileName = sys.argv[1]
modName = sys.argv[2]
dateName = sys.argv[3]

os.chdir("../");
os.system("./bin/pXar -v DEBUG  -g -T 35  -d data/"+modName+" -r ../"+modName+"data/"+fileName+"_"+modName+"_"+dateName+".root");
os.chdir("./data");

