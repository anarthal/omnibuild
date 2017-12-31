
import pickle
import hashlib

class Cache(object):
    def __init__(self):
        self.values = {}
    def load(self, fname):
        self.values = self._load(fname)
    def dump(self, fname):
        with open(fname, 'wb') as f:
            pickle.dump(self.values, f)
    def file_has_changed(self, fname):
        md5 = self._try_get_md5(fname)
        if md5 != self.values.get(fname, None):
            self.values[fname] = md5
            return True
        else:
            return False
    def file_store(self, fname):
        self.values[fname] = self._try_get_md5(fname)
    

    @staticmethod
    def _load(fname):
        try:
            with open(fname, 'rb') as f:
                res = pickle.load(f)
            if type(res) is dict:
                return res
            else:
                return {}
        except FileNotFoundError:
            return {}

    @staticmethod
    def _try_get_md5(fname):
        try:
            with open(fname, 'rb') as f:
                contents = f.read()
        except FileNotFoundError:
            return None
        md5 = hashlib.md5()
        md5.update(contents)
        return md5.digest()