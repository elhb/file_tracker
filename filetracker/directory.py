import os
import time
import sys
from filetracker.constants import *
from filetracker.config import *
from filetracker.mediafile import MediaFile
from filetracker.misc_functions import *

class Directory():
     
     def __init__(self, path, parent=None,verbose=False,followlinks=False):
          self.verbose = verbose
          assert os.path.isdir(path)
          self.name = os.path.abspath(path)
          if self.verbose: sys.stderr.write( 'INFO :: Creating new Directory Instance for {0}.\n'.format(self.name) )
          if USE_SPINNER: _junk = SPINNER.next()
          try: root, dirs, files = os.walk(path,followlinks=followlinks).next()
          except StopIteration: root, dirs, files = path,[],[]
          self.parent_dir = parent if parent else None
          self.dirs = [
                    Directory(os.path.join(root,directory), parent=self, verbose=self.verbose) for directory in dirs
               ]
          self.files = [
                    MediaFile(os.path.join(root,file_name),verbose=self.verbose) \
                    for file_name in files \
                    if '.'+file_name.split('.')[-1].lower() in AUDIO_EXTENSIONS+VIDEO_EXTENSIONS+IMAGE_EXTENSIONS
               ]

     def __str__(self,):
          return self.name
          
     def get_size(self,):
          return sum([_dir.get_size() for _dir in self.dirs]) + sum([media_file.size for media_file in self.files])
     
     @property
     def rdirs_count(self,):
          return sum([_dir.rdirs_count for _dir in self.dirs]) + len(self.dirs)

     @property
     def rfiles_count(self,):
          return sum([_dir.rfiles_count for _dir in self.dirs]) + len(self.files)

     @property
     def rfiles(self,):
          for _dir in self.dirs:
               for media_file in _dir.rfiles: yield media_file
          for media_file in self.files:
               yield media_file

     def printtree(
          self,
          nosize=False,
          levels=-1,
          header=True,
          level=0,
          includefiles=True,
          min_size=0,
          min_files=0,
          min_dups=0
          ):
          
          if header: print 'Size\tFiles\tFolders\tDups\tDups%\tPath'
          if levels == 0: return
          if nosize:
               b = 0
               human_size = 'NA'
               size_unit  = ''
          else:
               b  = self.get_size()
               human_size, size_unit = bytes2humanreadable(b)

          if nosize == False and b < min_size: pass
          elif self.rfiles_count < min_files: pass
          else:
               rdups_count = sum([1 for i in self.rfiles if len(i.duplicates)])
               rdups_percentage = round(100*float(rdups_count)/self.rfiles_count,2) if self.rfiles_count else 0.0
               if rdups_percentage < min_dups:pass
               else:
                    print '{0}{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format( human_size, size_unit, self.rfiles_count, self.rdirs_count , rdups_count, rdups_percentage, offset_name(self.name,level) )
          if level == 0: level = self.name.count('/')
          for directory in self.dirs:
               directory.printtree(
                    nosize=nosize,
                    levels=levels-1,
                    header=False,
                    level=level+1,
                    includefiles=includefiles,
                    min_size=min_size,
                    min_files=min_files
                    )

          if includefiles:
               for media_file in self.files:
                    if nosize == False and media_file.size < min_size: pass
                    else:
                         print '{0}{1}\t{2}\t{3}\t{4}\t{5}\t{6}'.format( media_file.human_size, media_file.size_unit, 1, 0 ,len(media_file.duplicates),'-', offset_name(media_file.fullpath,level+1) )

     @property
     def printdirs(self,):
          for i in range(len(self.dirs)): print '{0}. {1}'.format(i,self.dirs[i])
          
     @property
     def printfiles(self,):
          for i in range(len(self.files)): print '{0}. {1}'.format(i,self.files[i])
     
     def add_to_dup_tracker(self, files_sorted_by_md5sums):
          if self.verbose:
               _spinner = Spinner()
          for f in self.rfiles:
               if self.verbose: _spinner.next()
               files_sorted_by_md5sums=f.add_to_duplication_tracker(files_sorted_by_md5sums)
          if self.verbose: sys.stderr.write('\n')
          return files_sorted_by_md5sums