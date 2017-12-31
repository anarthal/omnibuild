import os.path

class Target(object):
    def __init__(self, name):
        self.name = name
        self.depends = []
    def __str__(self):
        return '<Target {}>'.format(self.name)
    def is_up_to_date(self, cache):
        raise NotImplementedError()
    def build(self):
        raise NotImplementedError()
    def update_cache(self, cache):
        pass


class ObjectFile(Target):
    def __init__(self, src, dirstack, compiler):
        Target.__init__(self, dirstack.get_output('obj', src + '.o'))
        self.src = src
        self.full_src = dirstack.join_real(src)
        self.compiler = compiler
        self.output = self.name
        if not os.path.isfile(self.full_src):
            raise FileNotFoundError('Source file {} does not exist'.format(self.full_src))
        self.includes = self.compiler.get_includes(self.full_src)
    def is_up_to_date(self, cache):
        if cache.file_has_changed(self.full_src):
            return False
        for inc in self.includes:
            if cache.file_has_changed(inc):
                return False
        return not cache.file_has_changed(self.output)
    def build(self):
        self.compiler.compile(self.full_src, self.output)
    def update_cache(self, cache):
        to_store = [self.full_src] + self.includes + [self.output]
        for fname in to_store:
            cache.file_store(fname)

class CppTarget(Target):
    def __init__(self, name, sources, dirstack, compiler):
        Target.__init__(self, dirstack.join_virtual(name))
        self.sources = sources
        self.output_file = self._get_output_file(name, dirstack)
        self.compiler = compiler
        self.objects = [ObjectFile(src, dirstack, compiler) for src in sources]
        self.libs = []
        self.depends = list(self.objects)
    def is_up_to_date(self, cache):
        return not cache.file_has_changed(self.output_file)
    def update_cache(self, cache):
        cache.file_store(self.output_file)
    def link_libraries(self, libs):
        to_add = libs
        for lib in libs:
            to_add += lib.libs
        self.libs += to_add
        self.depends += to_add

    def _get_link_inputs(self):
        return [obj.output for obj in self.objects] + [lib.output_file for lib in self.libs]
    def _get_output_file(self, name, dirstack):
        return dirstack.get_output('bin', name)

class Executable(CppTarget):
    def build(self):
        self.compiler.link_executable(self._get_link_inputs(), self.output_file)

class DynamicLibrary(CppTarget):
    def build(self):
        self.compiler.link_dynamic_library(self._get_link_inputs(), self.output_file)
    def _get_output_file(self, name, dirstack):
        return dirstack.get_output('bin', name +'.so')
