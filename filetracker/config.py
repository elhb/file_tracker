from filetracker.spinner import Spinner
import os

USE_SPINNER = True
SPINNER = Spinner()

KNOWNMD5S = dict()
if os.path.isfile('knownmd5s.tsv'):
    with open('knownmd5s.tsv') as infile:
        for line in infile:
            md5, filename = line.rstrip().split('\t')
            KNOWNMD5S[filename] = md5
