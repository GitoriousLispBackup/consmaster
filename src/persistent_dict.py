#!/usr/bin/python3
# -*- coding: utf-8 -*-


import pickle, os, shutil

class PersistentDict(dict):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    All three serialization formats are backed by fast C implementations.
    
    Adapted from python recipe, of Raymond Hettinger :
        http://code.activestate.com/recipes/576642/
    
    '''

    def __init__(self, filename, flag='c', mode=None):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb')
            with fileobj:
                self.load(fileobj)

    def sync(self):
        'Write dict to disk'
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def dump(self, fileobj):
        pickle.dump(dict(self), fileobj, 2)

    def load(self, fileobj):
        fileobj.seek(0)
        try:
            return self.update(pickle.load(fileobj))
        except Exception:
            raise ValueError('File not in a supported format')

