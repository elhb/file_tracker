from filetracker.spinner import Spinner
import os
import sys

USE_SPINNER = True
SPINNER = Spinner()

sys.stderr.write('INFO :: Loading precalculated md5 sums from disk.\n')
_s = Spinner()
KNOWNMD5S = dict()
if os.path.isfile('knownmd5s.tsv'):
    with open('knownmd5s.tsv') as infile:
        for line in infile:
            _s.next()
            md5, filename, modtime, source = line.rstrip().split('\t')
            if os.path.isfile(filename) and modtime == str(os.path.getmtime(filename)):
                KNOWNMD5S[filename] = md5
    sys.stderr.write('\nINFO :: Updating (removing duplicates from) precalculated md5 sums on disk.\n')
    _s = Spinner()
    printed={}
    with open('knownmd5s.tsv','w') as outfile:
        for filename, md5 in KNOWNMD5S.iteritems():
            if filename not in printed:
                _s.next()
                outfile.write('{0}\t{1}\t{2}\t{3}\n'.format(md5, filename,os.path.getmtime(filename),'K'))
                printed[filename]=True
sys.stderr.write('\nINFO :: Loaded and updated.\n\n')