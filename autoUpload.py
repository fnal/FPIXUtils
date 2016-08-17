#!/usr/bin/env python
import mechanize
import time
import argparse

parser = argparse.ArgumentParser(description='Upload zip files to Purdue DB')
parser.add_argument("-i", "--inputFiles", dest="inputFiles", nargs='+', help="Files to upload")
parser.add_argument("-u", "--user", dest="user", help="Name of user uploading results")
arguments = parser.parse_args()

loginURL = "http://www.physics.purdue.edu/cmsfpix/Submission_p/login.php?prev="
uploadURL = "http://www.physics.purdue.edu/cmsfpix/Submission_p/submit/batchallsubmit.php"

USERNAME = 'cmsfpix'
PASSWORD = 'd1c6e4a01f8a743d22d48fd824a5eb0636c616b4725fa872590652fe4ecb34400781785ec03b76f014d16e4eb72b13674a7dfe8e18470e10d566f2795831b5e7'

browser = mechanize.Browser()
browser.open(loginURL)

browser.select_form(nr=0)
browser.form['u'] = USERNAME
browser.form['p'] = PASSWORD
browser.submit()

for ifile in arguments.inputFiles:
    print "Uploading "+ifile
    start = time.time()
    browser.open(uploadURL)
    browser.select_form(nr=0)
    browser.form['user'] = arguments.user
    browser.form.add_file(open(ifile), 'text/plain', ifile)
    browser.submit()
    end = time.time()
    print "Upload of "+ifile+" took "+(end-start)+" seconds"
    time.sleep(10)

print "Done!"
