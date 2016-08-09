import mechanize
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-i", "--file", dest="inputFile",
                  help="path to input file")
parser.add_option("-u", "--user", dest="user",
                  help="Name of user uploading results")
(arguments, args) = parser.parse_args()

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

browser.open(uploadURL)
browser.select_form(nr=0)
browser.form['user'] = arguments.user
browser.form.add_file(open(arguments.inputFile), 'text/plain', arguments.inputFile)
browser.submit()
