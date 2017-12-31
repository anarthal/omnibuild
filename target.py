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
    def __init__(self, src, output, compiler):
        Target.__init__(self, output)
        self.src = src
        self.output = output
        self.compiler = compiler
        if not os.path.isfile(src):
            raise FileNotFoundError('Source file {} does not exist'.format(src))
        self.includes = self.compiler.get_includes(self.src)
    def is_up_to_date(self, cache):
        if cache.file_has_changed(self.src):
            return False
        for inc in self.includes:
            if cache.file_has_changed(inc):
                return False
        return not cache.file_has_changed(self.output)
    def build(self):
        self.compiler.compile(self.src, self.output)
    def update_cache(self, cache):
        to_store = [self.src] + self.includes + [self.output]
        for fname in to_store:
            cache.file_store(fname)

class CppTarget(Target):
    def __init__(self, name, sources, output_dir, compiler):
        Target.__init__(self, name)
        self.sources = sources
        self.output_dir = output_dir
        self.output_file = self._get_output_file()
        self.compiler = compiler
        self.objects = [self.make_object_file(src, output_dir, compiler) for src in sources]
        self.libs = []
        self.depends = list(self.objects)
        print('Name: {}, output_file: {}'.format(self.name, self.output_dir))
    def get_path(self):
        return self.output_file
    def is_up_to_date(self, cache):
        return not cache.file_has_changed(self.get_path())
    def update_cache(self, cache):
        cache.file_store(self.get_path())
    def link_libraries(self, libs):
        self.libs += libs
        self.depends += libs

    def _get_link_inputs(self):
        return [obj.output for obj in self.objects] + [lib.get_path() for lib in self.libs]
    def _get_output_file(self):
        return os.path.join(self.output_dir, 'bin', os.path.basename(self.name))

    @staticmethod
    def make_object_file(src, output_dir, compiler):
        return ObjectFile(src, os.path.join(output_dir, 'obj', src + '.o'), compiler)

class Executable(CppTarget):
    def build(self):
        self.compiler.link_executable(self._get_link_inputs(), self.get_path())

class DynamicLibrary(CppTarget):
    def build(self):
        self.compiler.link_dynamic_library(self._get_link_inputs(), self.get_path())
    def _get_output_file(self):
        return os.path.join(self.output_dir, 'bin', os.path.basename(self.name + '.so'))
