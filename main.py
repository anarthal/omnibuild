import compiler
import build
import networkx as nx
from matplotlib import pyplot as plt

def main():
    c = compiler.Compiler('i686-linux-gnu-g++-6')
    b = build.Build('output', c)
    exe = b.add_executable('myexe', ['myexe/main.cpp', 'myexe/other.cpp'])
    lib = b.add_dynamic_library('mylib', ['mylib/mylib.cpp'])
    exe.link_libraries([lib])
    b.build('output/targets/myexe')

main()
