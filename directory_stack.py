
from os import path

class Directory(object):
    __slots__ = ['real', 'virtual']
    def __init__(self, real, virtual=None):
        if virtual is None:
            virtual = real
        self.real = real
        self.virtual = virtual

class DirectoryStack(object):
    def __init__(self, output):
        self.output = output
        self._dirs = [Directory('.')]
    def push(self, real, virtual=None):
        self._dirs.append(Directory(real, virtual))
    def pop(self):
        assert(len(self._dirs) > 1)
        self._dirs.pop()
    def get_current_virtual(self):
        return path.normpath(path.join(*[d.virtual for d in self._dirs]))
    def get_current_real(self):
        return path.join(*[d.real for d in self._dirs])
    def join_virtual(self, *elms):
        return path.normpath(path.join(self.get_current_virtual(), *elms))
    def join_real(self, *elms):
        return path.join(self.get_current_real(), *elms)
    def get_output(self, *elms):
        return path.join(self.output, self.get_current_virtual(), *elms)
