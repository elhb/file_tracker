import hashlib
import random

# define a md5sum function
def md5(fname):
    try:
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except IOError:
        return ''.join([random.choice('1234567890ASDFGHJKLZZXCVBNMQWERTYUIOPqwertyuiopasdfghjklzxcvbnm') for i in xrange(20)])
