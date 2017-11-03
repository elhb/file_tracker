import os
import hashlib
import time
import re
import psutil
import sys
import sqlite3

# IMAGES
IMAGE_EXTENSIONS = [
     '.bmp',
     '.dib',
     '.gif',
     '.jpg',
     '.jpeg',
     '.jpe',
     '.jif',
     '.jfif',
     '.jfi',
     '.png',
     '.png',
     '.apng',
     '.crw',
     '.cr2',
     '.raw',
     '.rw2',
     '.nef',
     '.nrw',
     '.orf',
     '.tiff',
     '.tif',
     '.jp2',
     '.j2c',
     '.j2k',
     '.jpx',
     '.jpf',
     '.j2c',
     '.j2k',
     '.webp',
     '.svg',
     '.svgz',
     '.eps',
     '.epsi',
     '.epsf',
     '.pct',
     '.pict',
     '.pic',
     '.pcx',
     '.pdf',
     '.psd',
     '.pdd',
     '.tga',
     '.wmf',
     '.emf',
     '.wmz',
     '.emz'
     ]

# Audio
AUDIO_EXTENSIONS = [
     '.3gp',
     '.aa',
     '.aac',
     '.aax',
     '.act',
     '.aiff',
     '.amr',
     '.ape',
     '.au',
     '.awb',
     '.dct',
     '.dss',
     '.dvf',
     '.flac',
     '.gsm',
     '.iklax',
     '.ivs',
     '.m4a',
     '.m4b',
     '.m4p',
     '.mmf',
     '.mp3',
     '.mpc',
     '.msv',
     '.ogg',
     '.oga',
     '.mogg',
     '.opus',
     '.ra',
     '.rm',
     '.raw',
     '.sln',
     '.tta',
     '.vox',
     '.wav',
     '.wma',
     '.wv',
     '.webm',
     '.8svx'
     ]

# Video
VIDEO_EXTENSIONS = [
     '.webm',
     '.mkv',
     '.flv',
     '.flv',
     '.vob',
     '.ogv',
     '.ogg',
     '.drc',
     '.gif',
     '.gifv',
     '.mng',
     '.avi',
     '.mov',
     '.qt',
     '.wmv',
     '.yuv',
     '.rm',
     '.rmvb',
     '.asf',
     '.amv',
     '.mp4',
     '.m4p',
     '.m4v',
     '.mpg',
     '.mp2',
     '.mpeg',
     '.mpe',
     '.mpv',
     '.mpg',
     '.mpeg',
     '.m2v',
     '.m4v',
     '.svi',
     '.3gp',
     '.3g2',
     '.mxf',
     '.roq',
     '.nsv',
     '.flv',
     '.f4v',
     '.f4p',
     '.f4a',
     '.f4b'
     ]

files_sorted_by_md5sums = dict()

# define a md5sum function
def md5(fname):
     hash_md5 = hashlib.md5()
     with open(fname, "rb") as f:
         for chunk in iter(lambda: f.read(4096), b""):
             hash_md5.update(chunk)
     return hash_md5.hexdigest()

def bytes2humanreadable(b):
     kb =  b/1024.0
     Mb = kb/1024.0
     Gb = Mb/1024.0
     if   Gb >= 1.0: human_size, size_unit = (Gb, 'GB')
     elif Mb >= 1.0: human_size, size_unit = (Mb, 'MB')
     elif kb >= 1.0: human_size, size_unit = (kb, 'kb')
     elif b  >= 1.0: human_size, size_unit = (b , 'b' )
     else: human_size, size_unit = (b , 'b')
     human_size = round(human_size,1)
     return human_size, size_unit

def Spinner():
     counter = 0
     while True:
          if   counter%5 == 1: marker = '\\'
          elif counter%5 == 2: marker = '|'
          elif counter%5 == 3: marker = '/'
          elif counter%5 == 0: marker = '-'
          sys.stderr.write('Processed: {0} {1} files/dirs \r'.format(marker,counter))
          counter += 1
          yield counter

USE_SPINNER = True

SPINNER = Spinner()

class MediaFile():
     
     def __init__(self,file_name,verbose=False, duplication_tracking=False):
          self.verbose = verbose
          self.fullpath = os.path.abspath(file_name)
          self.filename = os.path.basename(self.fullpath)
          self.extension = self.fullpath.split('.')[-1] if self.fullpath.split('.') else None
          self._size = None
          self._md5 = None
          self.parent_dir = None
          self.duplicates = []
          if duplication_tracking: self.add_to_duplication_tracker()
          if USE_SPINNER: _junk = SPINNER.next()

     def add_to_duplication_tracker(self,):
          if self.md5_sum in files_sorted_by_md5sums:
               if self not in files_sorted_by_md5sums[self.md5_sum]:
                    for media_file in files_sorted_by_md5sums[self.md5_sum]:
                         self.duplicates.append( media_file )
                         media_file.duplicates.append( self )
                    files_sorted_by_md5sums[self.md5_sum].append( self )
          else:
               files_sorted_by_md5sums[self.md5_sum] = [ self ]

     @property
     def md5_sum(self,):
          if self._md5: return self._md5
          self._md5 = md5(self.fullpath)
          return self._md5

     @property
     def size(self):
          if not os.path.isfile(self.fullpath):
               sys.stderr.write( 'WARNING :: the file {0} is no longer present on disk, cannot fetch file size.\n'.format(self.fullpath) )
               return -1
          if self._size: return self._size
          if self.verbose: sys.stderr.write( 'INFO :: fetching file size for file {0}.\n'.format(self.fullpath) )
          self._size = os.path.getsize(self.fullpath)
          return self._size

     def get_stats(self,):
          return self.size,self.md5_sum

     def __str__(self,): return self.fullpath

     @property
     def human_size(self,):
          return bytes2humanreadable(self.size)[0]

     @property
     def size_unit(self,):
          return bytes2humanreadable(self.size)[1]

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
     
     def add_to_dup_tracker(self):
          if self.verbose:
               _spinner = Spinner()
          for f in self.rfiles:
               if self.verbose: _spinner.next()
               f.add_to_duplication_tracker()
          if self.verbose: sys.stderr.write('\n')

def offset_name(name,level):
     #offset = ' '.join('' for i in xrange(level))
     _parts = name.split('/')
     start = '|' if level != 0 else ''
     spacer = '/' if level != 0 else ''
     spacer2 = '`- ' if level != 0 else ''
     #return ''.join([ '|'+''.join([' ' for i in range(len(part))])    for part in _parts[1:max(0,level-1)] ]) + \
     return ''.join([ '|'+''.join([' ' for i in range(2)])    for part in _parts[1:max(0,level-1)] ]) + \
     spacer2 + \
     spacer+ '/'.join(_parts[level:])
     #''.join([' ' for i in range(len(_parts[max(0,level-1)]))]) + 

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
     root.add_to_dup_tracker()
     
     sys.stderr.write('INFO :: Adding path {} to the duplication tracker.\n'.format(path2))
     root2.verbose = True
     root2.add_to_dup_tracker()
     
     root.printtree(min_size=10*1024**2)
except KeyboardInterrupt:
     drop2interpreter()
finally:
     drop2interpreter()