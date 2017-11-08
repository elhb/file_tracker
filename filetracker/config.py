from filetracker.spinner import Spinner
import os
import sys

USE_SPINNER = True
SPINNER = Spinner(mem_intervall=1000)

sys.stderr.write('INFO :: Loading precalculated md5 sums from disk.\n')
_s = Spinner(update_intervall=1)
KNOWNMD5S = dict()
if os.path.isfile('knownmd5s.tsv'):
    with open('knownmd5s.tsv') as infile:
        for line in infile:
            _s.next()
            _tmp_parts = line.rstrip().split('\t')
            md5 = _tmp_parts[0]
            filename = _tmp_parts[1]
            modtime = _tmp_parts[2] if len(_tmp_parts) >= 3 else None
            source = _tmp_parts[3] if len(_tmp_parts) >= 4 else None
            #if os.path.isfile(filename) and (modtime == str(os.path.getmtime(filename)) or modtime == None):
            KNOWNMD5S[filename] = md5
    # sys.stderr.write('\nINFO :: Updating (removing duplicates from) precalculated md5 sums on disk.\n')
    # _s = Spinner()
    # printed={}
    # with open('knownmd5s.tsv','w') as outfile:
    #     for filename, md5 in KNOWNMD5S.iteritems():
    #         if filename not in printed:
    #             _s.next()
    #             outfile.write('{0}\t{1}\t{2}\t{3}\n'.format(md5, filename,os.path.getmtime(filename),'K'))
    #             printed[filename]=True
sys.stderr.write('\nINFO :: Loaded and updated.\n\n')