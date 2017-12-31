import compiler
import build

def main():
    c = compiler.Compiler('i686-linux-gnu-g++-6')
    b = build.Build('output', c)
    b.add_subdirectory('myexe')
    b.build('myexe/myexe')

main()
