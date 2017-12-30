import subprocess
import os

class Compiler(object):
    def __init__(self, exe='g++'):
        self.exe = exe
        self.flags = []
    def get_includes(self, src):
        args = [self.exe, '-M', '-MG', '-MM', src]
        output = subprocess.check_output(args).decode('ascii')
        res = output.replace('\\\n', ' ').replace('\n', ' ').split(' ')[2:]
        return list(filter(bool, res))
    def compile(self, src, output):
        args = [self.exe, '-c', '-fpic', '-o', output] + self.flags + [src]
        print('Building C++ source file {}'.format(src))
        self.make_containing_folder(output)
        subprocess.check_call(args)
    def link_executable(self, inputs, output):
        args = [self.exe, '-o', output] + inputs
        print('Linking C++ executable {}'.format(output))
        self.make_containing_folder(output)
        subprocess.check_call(args)
    def link_dynamic_library(self, inputs, output):
        args = [self.exe, '-shared', '-o', output] + inputs
        print('Linking C++ dynamic library {}'.format(output))
        self.make_containing_folder(output)
        subprocess.check_call(args)
    @staticmethod
    def make_containing_folder(output):
        os.makedirs(os.path.dirname(output), exist_ok=True)