import compiler
import build

def main():
    c = compiler.Compiler('i686-linux-gnu-g++-6')
    b = build.Build('output', c)
    b.add_subdirectory('mylib')
    b.add_subdirectory('myexe')
    b.build('output/myexe/bin/myexe')

main()
