import os
from filetracker.config import *
from filetracker.md5_sum import md5
from filetracker.misc_functions import *

class MediaFile():
     
    def __init__(self,file_name, parent=None,verbose=False):
        self.verbose = verbose
        self.fullpath = os.path.abspath(file_name)
        #self.filename = os.path.basename(self.fullpath)
#        self.extension = self.fullpath.split('.')[-1] if self.fullpath.split('.') else None
        self._size = None
#        self._md5 = None
        self.parent_dir = parent
#        self.duplicates = []
        if USE_SPINNER: _junk = SPINNER.next()

    @property
    def extension(self,):
        return self.fullpath.split('.')[-1] if self.fullpath.split('.') else None

    @property
    def filename(self,):
        return os.path.basename(self.fullpath)

    @property
    def duplicates(self,):
        return [ duplicate for duplicate in self.files_by_md5_pointer[self.md5_sum] if duplicate != self ]

    def add_to_duplication_tracker(self,files_sorted_by_md5sums, _spinner=None):
        if not self.md5_sum: return files_sorted_by_md5sums # will not be added to tracker if not md5 sum is available
        if self.md5_sum in files_sorted_by_md5sums:
            if self not in files_sorted_by_md5sums[self.md5_sum]:
                #for media_file in files_sorted_by_md5sums[self.md5_sum]:
                #    self.duplicates.append( media_file )
                #    media_file.duplicates.append( self )
                files_sorted_by_md5sums[self.md5_sum].append( self )
        else:
            files_sorted_by_md5sums[self.md5_sum] = [ self ]
        if _spinner: _spinner.next()
        self.files_by_md5_pointer = files_sorted_by_md5sums
        return files_sorted_by_md5sums

    @property
    def md5_sum(self,):
        try:
            return KNOWNMD5S[self.fullpath].rstrip()
        except KeyError:
            if '_md5' in self.__dict__ and self._md5: return self._md5
            sys.stderr.write('WARNING :: {} is not known atempting to fetch md5 sum.\n'.format(self.fullpath))
            self._md5 = md5(self.fullpath).rstrip()
            if self._md5:
                with open('knownmd5s.tsv','a') as outfile: outfile.write('{0}\t{1}\t{2}\t{3}\n'.format(self._md5, self.fullpath,os.path.getmtime(self.fullpath),'M'))
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
