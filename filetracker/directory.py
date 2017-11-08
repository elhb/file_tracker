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
          self.dirs = []
          for directory in dirs:
               
               # skip empty dirs
               # should maybe make this recursive so that if there are no files around skip the full branch
               _tmp = sum([len(info[-1]) for info in os.walk(os.path.join(root,directory))]) # gets the recursive file count
               #try: _tmp_list1,_tmplist2 = os.walk(os.path.join(root,directory),followlinks=followlinks).next()[1:]
               #except StopIteration: _tmp_list1,_tmplist2 = [],[]
               #_empty = not sum([len(_tmp_list1),len(_tmplist2)])
               _empty = not _tmp
               
               if not os.path.islink(os.path.join(root,directory)) and not _empty:
                    self.dirs.append( Directory(os.path.join(root,directory), parent=self, verbose=self.verbose) )
          self.files = [
                    MediaFile(os.path.join(root,file_name),parent=self, verbose=self.verbose) \
                    for file_name in files if not os.path.islink(os.path.join(root,file_name))
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
          min_dups=0,
          skip_subs_of_dups=True,
          sugessted_actions = None
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
                    out_str = '{0}{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format( human_size, size_unit, self.rfiles_count, self.rdirs_count , rdups_count, rdups_percentage, offset_name(self.name,level),' '.join(d.name for d in self.duplicates) )
                    print out_str
                    if self.duplicates:
                         if not sugessted_actions or self not in sugessted_actions:
                              with open('actions.txt','a') as outfile: outfile.write('# {}\nrm -vr "{}"\n'.format(out_str,self.name))
                         if not sugessted_actions: sugessted_actions = dict()
                         sugessted_actions[self] = True
                         for duplicate in self.duplicates: sugessted_actions[duplicate] = True
          if level == 0: level = self.name.count('/')

          if skip_subs_of_dups and self.duplicates: return

          for directory in self.dirs:
               directory.printtree(
                    nosize=nosize,
                    levels=levels-1,
                    header=False,
                    level=level+1,
                    includefiles=includefiles,
                    min_size=min_size,
                    min_files=min_files,
                    skip_subs_of_dups=skip_subs_of_dups,
                    sugessted_actions=sugessted_actions
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

     def add_to_dup_tracker(self, files_sorted_by_md5sums, _spinner=None):
          if self.verbose and not _spinner: _spinner = Spinner(update_intervall=1)
          
          for f in self.files:
               #if self.verbose: _spinner.next()
               files_sorted_by_md5sums=f.add_to_duplication_tracker(files_sorted_by_md5sums, _spinner=_spinner)
          if self.verbose: sys.stderr.write('\n')
          
          if not self.files:
               key='{}__{}'.format(self.get_size(),len(list(self.rfiles))+len(list(self.rdirs)) )
               try:            files_sorted_by_md5sums['NOFILES'][key].append(self)
               except KeyError:files_sorted_by_md5sums['NOFILES'][key] = [self]
               if self.verbose:_spinner.next()
          for _dir in self.dirs:
               files_sorted_by_md5sums = _dir.add_to_dup_tracker(files_sorted_by_md5sums,_spinner=_spinner)
               # if not _dir.files:
               #      key='{}__{}'.format(_dir.get_size(),len(list(_dir.rfiles))+len(list(_dir.rdirs)) )
               #      try:            files_sorted_by_md5sums['NOFILES'][key].append(_dir)
               #      except KeyError:files_sorted_by_md5sums['NOFILES'][key] = [_dir]
               #      if self.verbose:_spinner.next()
          
          return files_sorted_by_md5sums

     def isduplicate(self,directory,recurion_depth=0,files_sorted_by_md5sums={}):

          if compare_files_in_directories(self,directory,recurion_depth=recurion_depth) and compare_files_in_directories(directory,self,recurion_depth=recurion_depth):
               pass#sys.stderr.write( 'INFO :: All files in directory {0} are dupliacted in dir {1} and vice versa.\n'.format(self,directory) )
          else: return False

          if compare_subdirs_in_directories(self,directory,recurion_depth=recurion_depth,files_sorted_by_md5sums=files_sorted_by_md5sums) and compare_subdirs_in_directories(directory,self,recurion_depth=recurion_depth,files_sorted_by_md5sums=files_sorted_by_md5sums):
               #sys.stderr.write( 'INFO :: All subdirs in directory {0} are dupliacted in dir {1} and vice versa.\n'.format(self,directory) )
               return True
          else: return False

     def find_duplicates(self,recurion_depth=0,files_sorted_by_md5sums={}):

          recurion_depth_offset=''.join([' ' for i in xrange(4*recurion_depth)])+str(recurion_depth)+'-'
          sys.stderr.write( 'INFO :: {}Directory {} Cheking children.\n'.format(recurion_depth_offset,self.name) )
          for directory in self.dirs:
               if not directory.dup_checked:
                    sys.stderr.write( 'INFO :: {}Need to check child of potential duplicate first ... going to child\n'.format(recurion_depth_offset))
                    directory.find_duplicates(recurion_depth=recurion_depth+1,files_sorted_by_md5sums=files_sorted_by_md5sums)
          sys.stderr.write( 'INFO :: {}Directory {} all children checked moving on with self.\n'.format(recurion_depth_offset,self.name) )

          sys.stderr.write( 'INFO :: {}Directory {} searching for potential duplicates.\n'.format(recurion_depth_offset,self.name) )
          potential_duplicates = {}
          for _file in self.files:
               for duplicate in _file.duplicates:
                    if duplicate.parent_dir.name != self.name:
                         potential_duplicates[duplicate.parent_dir] = None
          # NEED FIX #################################################################################
          # CANNOT FIND POTENTIAL DUPLICATE OF A FOLDER WITH ONLY SUBDIRS NO FILES.                  #
          if not self.files:                                                                         #
               key='{}__{}'.format(self.get_size(),len(list(self.rfiles))+len(list(self.rdirs)) )
               try:                                                                                  #
                    _tmp = files_sorted_by_md5sums['NOFILES'][key]                       #
               except KeyError:                                                                      #
                    sys.stderr.write('WARNING :: {} dir size not in NOFILES ({}) the key {} is not in dict.\n'.format(recurion_depth_offset,self.name,key))
                    _tmp = []
               for potential_duplicate in _tmp:                                                      #
                    if potential_duplicate.name != self.name:                                        #
                         potential_duplicates[potential_duplicate] = None                            #
          ############################################################################################

          sys.stderr.write( 'INFO :: {}Found {} potential duplicates validating.\n'.format(recurion_depth_offset,len(potential_duplicates)) )
          _tmp_counter = 0
          for potential_duplicate in potential_duplicates.keys():
               _tmp_counter += 1
               sys.stderr.write( 'INFO :: {}--Comparing to potential duplicate {}. {}.\n'.format(recurion_depth_offset,_tmp_counter,potential_duplicate.name) )
               if potential_duplicate in self.rdirs:
                    sys.stderr.write( 'INFO :: {}----Directories are NOT duplicates (child of parent).\n'.format(recurion_depth_offset) )
                    continue

               if self in potential_duplicate.duplicates and potential_duplicate in self.duplicates:
                    sys.stderr.write( 'INFO :: {}----Directories are duplicates (compared earlier).\n'.format(recurion_depth_offset) )
                    continue

               if self.isduplicate(potential_duplicate,recurion_depth=recurion_depth,files_sorted_by_md5sums=files_sorted_by_md5sums):
                    self.duplicates.append(potential_duplicate)
                    potential_duplicate.duplicates.append(self)
                    sys.stderr.write(  'INFO :: {}----Directories are duplicates.\n'.format(recurion_depth_offset) )
               else: sys.stderr.write( 'INFO :: {}----Directories are NOT duplicates.\n'.format(recurion_depth_offset) )

#          sys.stderr.write( '\n')

          sys.stderr.write( 'INFO :: {}Directory {} dup check complete.\n'.format(recurion_depth_offset,self.name) )
          self.dup_checked = True
          return

def compare_files_in_directories(reference_dir,subject_dir,verbose=False,recurion_depth=0):
     if verbose:
          sys.stderr.write('INFO ::         Comparing files.\n')
          sys.stderr.write('INFO ::         referencedir={}\n'.format(reference_dir.name))
          sys.stderr.write('INFO ::         subjectdir={}\n'.format(subject_dir.name))
     all_files_form_self_is_duplicated_in_other_dir = True

     if len(reference_dir.files) != len(subject_dir.files): return False

     for _file1 in reference_dir.files:

          _file1_duplicated_in_other_dir = False
          for _file2 in subject_dir.files:
               if _file1 in _file2.duplicates and _file2 in _file1.duplicates:
                    _file1_duplicated_in_other_dir = True
                    break

          if not _file1_duplicated_in_other_dir:
               all_files_form_self_is_duplicated_in_other_dir = False
               if verbose:sys.stderr.write('WARNING ::         file {} in reference is NOT present in subject.\n'.format(_file1.filename) )
          else:
               if verbose:sys.stderr.write('INFO ::         file {} in reference is also in subject {}.\n'.format(_file1.filename,_file2.filename) )

     if all_files_form_self_is_duplicated_in_other_dir:
          if verbose:sys.stderr.write( 'INFO ::         All files in reference are dupliacted in subject.\n')
          return True
     else:
          if verbose:sys.stderr.write( 'WARNING ::         Some files in reference are NOT dupliacted in subject.\n')
          return False

def compare_subdirs_in_directories(reference_dir,subject_dir,verbose=False,recurion_depth=0,files_sorted_by_md5sums={}):

     if verbose:
          sys.stderr.write('INFO ::         Comparing sub directories.\n')
          sys.stderr.write('INFO ::         referencedir={}\n'.format(reference_dir.name))
          sys.stderr.write('INFO ::         subjectdir={}\n'.format(subject_dir.name))

     if len(reference_dir.dirs) == len(subject_dir.dirs):
          if len(reference_dir.dirs) == 0:
                    if verbose: sys.stderr.write( 'INFO ::         All sub directories in reference are dupliacted in subject and vice versa (because there are none).\n' )
                    return True
          else:
               for directory in reference_dir.dirs+subject_dir.dirs:
                    if directory in [reference_dir, subject_dir]:
                         sys.stderr.write( 'WARNING :: one dir in comparison is a child of a dir in the comparison.\n' )
                         continue
                    if not directory.dup_checked:
                         sys.stderr.write( 'INFO ::         Need to check child of potential duplicate first ...\n' )
                         directory.find_duplicates(recurion_depth=recurion_depth+1,files_sorted_by_md5sums=files_sorted_by_md5sums)

               all_subdirs_form_self_is_duplicated_in_other_dir = True
               for _subdir1 in reference_dir.dirs:

                    _subdir1_duplicated_in_other_dir = False
                    for _subdir2 in subject_dir.dirs:
                         if _subdir1 in _subdir2.duplicates and _subdir2 in _subdir1.duplicates:
                              _subdir1_duplicated_in_other_dir = True
                              break

                    if not _subdir1_duplicated_in_other_dir:
                         all_subdirs_form_self_is_duplicated_in_other_dir = False
                         if verbose:sys.stderr.write('WARNING ::         subdir {} in reference is not present in subject.\n'.format(_subdir1.name) )
                    else:
                         if verbose:sys.stderr.write('INFO ::         subdir {} in reference is also in subject {}.\n'.format(_subdir1.name,_subdir2.name) )

               if all_subdirs_form_self_is_duplicated_in_other_dir:
                    if verbose:sys.stderr.write( 'INFO ::         All subdirs in reference are dupliacted in subject.\n')
                    return True
               else:
                    if verbose:sys.stderr.write( 'WARNING ::         Some subdirs in reference are NOT dupliacted in subject.\n')
                    return False
     else:
          if verbose: sys.stderr.write( 'WARNING ::         The number of sub directories in refernce do NOT match the number in subject.\n')
          return False
