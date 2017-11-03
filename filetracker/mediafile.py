import os
from filetracker.config import *
from filetracker.md5_sum import md5
from filetracker.misc_functions import *

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

    def add_to_duplication_tracker(self,files_sorted_by_md5sums):
        if self.md5_sum in files_sorted_by_md5sums:
            if self not in files_sorted_by_md5sums[self.md5_sum]:
                for media_file in files_sorted_by_md5sums[self.md5_sum]:
                    self.duplicates.append( media_file )
                    media_file.duplicates.append( self )
                files_sorted_by_md5sums[self.md5_sum].append( self )
        else:
            files_sorted_by_md5sums[self.md5_sum] = [ self ]
        return files_sorted_by_md5sums

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
