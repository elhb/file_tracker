import os
import sys

from filetracker.constants import *
from filetracker.config import *
from filetracker.directory import Directory

files_sorted_by_md5sums = dict()

def drop2interpreter():
     import code
     code.interact(local=dict(globals(), **locals()))

try:
     path = '/home'
     sys.stderr.write('INFO :: Loading all directories and files recursively in path {}: \n'.format(path))
     root = Directory(path)
     sys.stderr.write('\n')
     root.printtree(min_size=1024**3)
     
     path2 = '/media'
     sys.stderr.write('INFO :: Loading all directories and files recursively in path {}: \n'.format(path))
     root2 = Directory(path2)
     sys.stderr.write('\n')
     root2.printtree(min_size=1024**3)
     
     sys.stderr.write('INFO :: Adding path {} to the duplication tracker.\n'.format(path))
     root.verbose = True
     files_sorted_by_md5sums = root.add_to_dup_tracker(files_sorted_by_md5sums)
     
     sys.stderr.write('INFO :: Adding path {} to the duplication tracker.\n'.format(path2))
     root2.verbose = True
     files_sorted_by_md5sums = root2.add_to_dup_tracker(files_sorted_by_md5sums)
     
     root.printtree(min_size=10*1024**2)
     root2.printtree(min_size=10*1024**2)
except KeyboardInterrupt:
     drop2interpreter()


drop2interpreter()