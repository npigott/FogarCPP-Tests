#!/bin/python
import sys, os, subprocess

from optparse import OptionParser
from subprocess import Popen, PIPE, STDOUT



# Get the interpreter from optparse
parser = OptionParser(usage="Usage: %prog [options] interpreter")
#parser.add_option("-i", "--inter", metavar="NAME", dest="interpreter",
#                  help="the name of the interpreter to run tests for") 
parser.add_option("-q", "--quiet", dest="verbose", action="store_false", default=False,
                  help="don't print status messages to stdout")
parser.add_option("-t", "--tests", metavar="DIR", dest="testdir",
                  help="the directory tests are located in, defaulting to $FCPPTESTS") 
(options, args) = parser.parse_args()
if options.testdir is None:
  if 'FCPPTESTS' in os.environ:
    options.testdir = os.environ['FCPPTESTS']
  else:
    sys.exit('Error: test directory not specified in options or $FCPPTESTS environment variable.')
if not os.path.exists(options.testdir):
  sys.exit('Error: test directory is not valid.')
options.testdir = os.path.abspath(options.testdir)

if len(args) >= 1:
  (interp_dir, interp_name) = os.path.split(args[0])
else:
  sys.exit('Error: no interpreter provided in arguments.')

if options.verbose:
  print "Testing interpreter: "+ interp_name

# Check if executable exists
os.chdir(interp_dir)


if not os.path.isfile(os.getcwd() + "/" + interp_name):
  # Attempt to run the MAKEFILE
  if options.verbose:
    print "Executable not found, compiling using MAKEFILE..."
    make = subprocess.check_call("make")
  else:
    make = subprocess.Popen("make", stdout=PIPE, stderr=STDOUT)
    out = make.communicate()[0]
elif options.verbose:
  print "Executable found, skipping MAKE"

if not os.path.isfile(os.getcwd() + "/" + interp_name):
  sys.exit('Executable cannot be found or made.')




# Grab all files from the $FCPPTESTS directory that are of the proper format
files = []
count = 0
for file in os.listdir(options.testdir):
  if file.endswith(".fcpp"):
    files.append(os.path.join(options.testdir, file))
    count += 1
if options.verbose:
  print "Found", count, "test cases."

# Run throught each test file
anywrong = False
for fname in files:
  file = open(fname, "r")
  case = "Undefined"
  output = []
  casenames = []
  # Parse the input file into input and output lists, also grab the case name
  in_output = False
  for line in file:
   if line.startswith("--Case Name"):
     case = line[13:].strip()
   elif line.startswith("--Output:"):
     in_output = True
   elif line.startswith("--End Output"):
     in_output = False
   elif line.startswith("--") and in_output:
     tmp = line[2:]
     if tmp is not None:
        output.append(tmp.strip())
        casenames.append(case)
  file.close
  file = open(fname, "r")
  # Perform all the calculations and compare them to the expected output
  p = subprocess.Popen(("./" + interp_name), stdin=file, stdout=PIPE, stderr=STDOUT)
  out = p.communicate()[0].splitlines()
  wrong = 0
  if len(out) > len(output):
    print "Warning: More lines output that specified in file."
  for i in range(0, len(output)):
    if i >= len(out):
      print "Test case ", casenames[i], " missing on output " , i, ", expected ", output[i]+ "."
    elif not output[i] == out[i].strip():
      if wrong == 0:
        print "On File", os.path.basename(fname)
      wrong += 1
      anywrong = True
      print "Test case", casenames[i], "wrong on output" , str(i) + ", expected", output[i], "but got", out[i].strip()+ "."
  if wrong > 0:
    print "Test case", casenames[i], "wrong on",wrong,"cases."
  elif options.verbose:
    print "Test case",  casenames[i], "correct!"

if not anywrong:
  print "All test cases passed succesfully!"
