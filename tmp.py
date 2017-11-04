import os
import sys
import time

from filetracker.constants import *
from filetracker.config import *
from filetracker.directory import Directory

files_sorted_by_md5sums = dict()

def drop2interpreter():
     sys.stderr.write('INFO :: KeyboardInterrupt, dropping to interpreter ...\n')
     import code
     code.interact(local=dict(globals(), **locals()))

try:
     try:
          path = sys.argv[1]
          sys.stderr.write('INFO :: Loading all directories and files recursively in path {}: \n'.format(path))
          root = Directory(path)
          sys.stderr.write('\n\n')
     except IndexError:
          root = None

     try:
          path2 = sys.argv[2]
          sys.stderr.write('INFO :: Loading all directories and files recursively in path {}: \n'.format(path2))
          reference_directory = Directory(path2)
          sys.stderr.write('\n\n')
     except IndexError:
          reference_directory = None

     sys.stderr.write('INFO :: Adding path {} to the duplication tracker.\n'.format(path))
     root.verbose = True
     files_sorted_by_md5sums = root.add_to_dup_tracker(files_sorted_by_md5sums)
     sys.stderr.write('\n')

     if reference_directory:
          sys.stderr.write('INFO :: Adding path {} to the duplication tracker.\n'.format(path2))
          reference_directory.verbose = True
          files_sorted_by_md5sums = reference_directory.add_to_dup_tracker(files_sorted_by_md5sums)
          sys.stderr.write('\n')

     root.find_duplicates()
     sys.stderr.write('\n')

     # root.printtree(includefiles=False,min_size=100*1024**2)
     root.printtree(includefiles=False)
     sys.stderr.write('\n')

     sys.stderr.write('INFO :: Sleeping few a minutes before exiting.\n')
     final_sleep = 600
     for i in xrange(final_sleep):
          sys.stderr.write('\t{}\tseconds to the end.\r'.format(final_sleep-i))
          time.sleep(1)

except KeyboardInterrupt:
     sys.stderr.write('\n\n')
     drop2interpreter()