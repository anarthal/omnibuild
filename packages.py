import json
import abc

class PackageManager(object):
    def __init__(self, providers=[]):
        self.providers = providers

    def find_package(self, name, build):
        for prov in self.providers:
            pkg = prov.find(name)
            if pkg is not None:
                pkg.configure(build)
                return
        raise ValueError('Package {} not found'.format(name))
    
    @staticmethod
    def load(fname):
        with open(fname, 'r') as f:
            obj = json.load(f)
        provs = [PackageManager.create_provider(prov) for prov in obj]
        return PackageManager(provs)
    @staticmethod
    def create_provider(obj):
        if obj['type'] != 'local':
            raise ValueError('Unknown package provider type')
        return LocalProvider(obj)
    
class LocalProvider(object):
    def __init__(self, obj):
        self.packages = obj['packages']
    def find(self, name):
        res = self.packages.get(name, None)
        if res is None:
            return res
        else:
            return OmibuildPackage(name, res['path'])

class OmibuildPackage(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
    def configure(self, build):
        build.add_subdirectory(self.path, vpath=self.name)
