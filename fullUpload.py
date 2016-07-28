from glob import glob
import os
import subprocess
import sys

os.system("python2.6 ~/Testing/FPIXUtils/zipUpload.py "+sys.argv[1]);
os.system("python2.6 ~/Testing/FPIXUtils/tarUpload.py "+sys.argv[1]);
