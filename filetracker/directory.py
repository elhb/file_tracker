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
                    MediaFile(os.path.join(root,file_name),parent=self, verbose=self.verbose) \
                    for file_name in files #\
                    #if '.'+file_name.split('.')[-1].lower() in AUDIO_EXTENSIONS+VIDEO_EXTENSIONS+IMAGE_EXTENSIONS
               ]
          self.duplicates = []
          self.dup_checked = False

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
          returned = dict()
          for _dir in self.dirs:
               for media_file in _dir.rfiles:
                    if media_file not in returned:
                         yield media_file
                         returned[media_file]=True
          for media_file in self.files:
                    if media_file not in returned:
                         yield media_file
                         returned[media_file]=True

     @property
     def rdirs(self,):
          returned = dict()
          for _dir in self.dirs:
               for _grand_child_dir in _dir.dirs:
                    if _grand_child_dir not in returned:
                         yield _grand_child_dir
                         returned[_grand_child_dir] = True
          for _dir in self.dirs:
               if _dir not in returned:
                    yield _dir
                    returned[_dir] = True


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
          
          if header: print 'Size\tFiles\tFolders\tDups\tDups%\tPath\tDup locations'
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
                    print '{0}{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format( human_size, size_unit, self.rfiles_count, self.rdirs_count , rdups_count, rdups_percentage, offset_name(self.name,level),'-' )
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
                         print '{0}{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format( media_file.human_size, media_file.size_unit, 1, 0 ,len(media_file.duplicates),'-', offset_name(media_file.fullpath,level+1), ' '.join(f.fullpath for f in media_file.duplicates) )

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
     
     def isduplicate(self,directory):
          
          if compare_files_in_directories(self,directory) and compare_files_in_directories(directory,self):
               pass#sys.stderr.write( 'INFO :: All files in directory {0} are dupliacted in dir {1} and vice versa.\n'.format(self,directory) )
          else: return False
          
          if compare_subdirs_in_directories(self,directory) and compare_subdirs_in_directories(directory,self):
               #sys.stderr.write( 'INFO :: All subdirs in directory {0} are dupliacted in dir {1} and vice versa.\n'.format(self,directory) )
               return True
          else: return False

     def find_duplicates(self,):
          
          for directory in self.dirs:
               if not directory.dup_checked: directory.find_duplicates()
          
          sys.stderr.write( 'INFO :: directory {} searching for potential duplicates.\n'.format(self.name) )
          potential_duplicates = {}
          for _file in self.files:
               for duplicate in _file.duplicates:
                    potential_duplicates[duplicate.parent_dir] = None
          
          sys.stderr.write( 'INFO :: Found {} potential duplicates validating.\n'.format(len(potential_duplicates)) )
          for potential_duplicate in potential_duplicates.keys():
               sys.stderr.write( 'INFO :: Comparing to potential duplicate {}.\n'.format(potential_duplicate.name) )

               if self in potential_duplicate.duplicates and potential_duplicate in self.duplicates:
                    sys.stderr.write( 'INFO :: Directories are duplicates.\n'.format(self.name,potential_duplicate.name) )
                    continue

               if self.isduplicate(potential_duplicate):
                    self.duplicates.append(potential_duplicate)
                    potential_duplicate.duplicates.append(self)
                    sys.stderr.write( 'INFO :: Directories are duplicates.\n'.format(self.name,potential_duplicate.name) )
               else: sys.stderr.write( 'INFO :: Directories are NOT duplicates.\n'.format(self.name,potential_duplicate.name) )

               sys.stderr.write( '\n')
          
          self.dup_checked = True
          
def compare_files_in_directories(reference_dir,subject_dir,verbose=False):
     if verbose:
          sys.stderr.write('INFO :: Comparing files.\n')
          sys.stderr.write('INFO :: referencedir={}\n'.format(reference_dir.name))
          sys.stderr.write('INFO :: subjectdir={}\n'.format(subject_dir.name))
     all_files_form_self_is_duplicated_in_other_dir = True

     for _file1 in reference_dir.files:

          _file1_duplicated_in_other_dir = False
          for _file2 in subject_dir.files:
               if _file1 in _file2.duplicates and _file2 in _file1.duplicates:
                    _file1_duplicated_in_other_dir = True
                    break
          
          if not _file1_duplicated_in_other_dir:
               all_files_form_self_is_duplicated_in_other_dir = False
               if verbose:sys.stderr.write('WARNING :: file {} in reference is NOT present in subject.\n'.format(_file1.filename) )
          else:
               if verbose:sys.stderr.write('INFO :: file {} in reference is also in subject {}.\n'.format(_file1.filename,_file2.filename) )
     
     if all_files_form_self_is_duplicated_in_other_dir:
          if verbose:sys.stderr.write( 'INFO :: All files in reference are dupliacted in subject.\n')
          return True
     else:
          if verbose:sys.stderr.write( 'WARNING :: Some files in reference are NOT dupliacted in subject.\n')
          return False

def compare_subdirs_in_directories(reference_dir,subject_dir,verbose=True):

     if verbose:
          sys.stderr.write('INFO :: Comparing sub directories.\n')
          sys.stderr.write('INFO :: referencedir={}\n'.format(reference_dir.name))
          sys.stderr.write('INFO :: subjectdir={}\n'.format(subject_dir.name))

     if len(reference_dir.dirs) == len(subject_dir.dirs):
          if len(reference_dir.dirs) == 0:
                    if verbose: sys.stderr.write( 'INFO :: All sub directories in reference are dupliacted in subject and vice versa (because there are none).\n' )
                    return True
          else:
               for directory in reference_dir.dirs+subject_dir.dirs:
                    if not directory.dup_checked:
                         sys.stderr.write( 'INFO :: Need to check child of potential duplicate first ...\n' )
                         directory.find_duplicates()

               all_subdirs_form_self_is_duplicated_in_other_dir = True
               for _subdir1 in reference_dir.rdirs:
          
                    _subdir1_duplicated_in_other_dir = False
                    for _subdir2 in subject_dir.rdirs:
                         if _subdir1 in _subdir2.duplicates and _subdir2 in _subdir1.duplicates:
                              _subdir1_duplicated_in_other_dir = True
                              break
                    
                    if not _subdir1_duplicated_in_other_dir:
                         all_subdirs_form_self_is_duplicated_in_other_dir = False
                         if verbose:sys.stderr.write('WARNING :: subdir {} in reference is not present in subject.\n'.format(_subdir1.name) )
                    else:
                         if verbose:sys.stderr.write('INFO :: subdir {} in reference is also in subject {}.\n'.format(_subdir1.name,_subdir2.name) )
               
               if all_files_form_self_is_duplicated_in_other_dir:
                    if verbose:sys.stderr.write( 'INFO :: All subdirs in reference are dupliacted in subject.\n')
                    return True
               else:
                    if verbose:sys.stderr.write( 'WARNING :: Some subdirs in reference are NOT dupliacted in subject.\n')
                    return False
     else:
          if verbose: sys.stderr.write( 'WARNING :: The number of sub directories in refernce do NOT match the number in subject.\n')
          return False