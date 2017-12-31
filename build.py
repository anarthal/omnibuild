
import target
import cache
from directory_stack import DirectoryStack

import networkx as nx
import os.path
import importlib

class Build(object):
    def __init__(self, output, compiler):
        self.dirstack = DirectoryStack()
        self.targets = {}
        self.output = output
        self.compiler = compiler
        self.cache = cache.Cache()
        self.cache.load(self._cache_path())
    
    def add_target(self, elm):
        print('Adding target {}'.format(elm.name))
        self.targets[elm.name] = elm
    def add_executable(self, name, srcs):
        return self._add_cpp_target(name, srcs, target.Executable)
    def add_dynamic_library(self, name, srcs):
        return self._add_cpp_target(name, srcs, target.DynamicLibrary)
    def add_subdirectory(self, directory, script='configure.py'):
        self.dirstack.push(directory)
        script_path = self.dirstack.join_real(script)
        if not os.path.isfile(script_path):
            raise FileNotFoundError('Unable to find configure script ' + script_path)
        loader = importlib.machinery.SourceFileLoader('configure', script_path)
        module = loader.load_module('configure')
        module.configure(self)
        self.dirstack.pop()

    def make_build_graph(self, target):
        return BuildGraph(self.targets, target, self.cache)

    def build(self, target):
        self.make_build_graph(target).build()
        self.cache.dump(self._cache_path())

    def _add_cpp_target(self, name, srcs, target_class):
        actual_srcs = [self.dirstack.join_real(src) for src in srcs]
        actual_name = self.dirstack.join_virtual(post=name)
        actual_output = self.dirstack.join_virtual(pre=self.output)
        target = target_class(actual_name, actual_srcs, actual_output, self.compiler)
        self.add_target(target)
        for obj in target.objects:
            self.add_target(obj)
        return target
    def _cache_path(self):
        return os.path.join(self.output, '__omnibuild_cache.dat')



class TargetNode(object):
    def __init__(self, target, in_degree):
        self.target = target
        self.remaining = in_degree
        self.built = False
        self.clean = True
    def is_buildable(self):
        return self.remaining == 0
    def is_clean(self, cache):
        return self.clean and self.target.is_up_to_date(cache)

class BuildGraph(object):
    def __init__(self, targets, current_target, cache):
        self.targets = targets
        self.graph = self._make_graph(targets.values())
        self.current_target = self.targets[current_target]
        self.cache = cache

        to_build = nx.ancestors(self.graph, self.current_target)
        to_build.add(self.current_target)
        in_degrees = self.graph.in_degree(to_build)
        self.nodes = { target.name: TargetNode(target, in_degrees[target]) for target in to_build }

    def draw(self):
        nx.draw(self.graph, with_labels=True)
        import matplotlib.pyplot as plt
        plt.show()

    def get_buildable_targets(self):
        return [node for node in self.nodes.values() if node.is_buildable()]

    def build_target(self, target_node):
        if not target_node.is_buildable():
            raise ValueError('{} is not buildable'.format(target_node.target))
        
        if not target_node.is_clean(self.cache):
            target_node.target.build()
            target_node.target.update_cache(self.cache)
            clean = False
        else:
            clean = True
        target_node.built = True

        sucs = self.graph.successors(target_node.target)
        sucs_nodes = [ self.nodes[suc.name] for suc in sucs ]
        for node in sucs_nodes:
            node.remaining -= 1
            if not clean:
                node.clean = False
        return [node for node in sucs_nodes if node.is_buildable()]

    def is_build_complete(self):
        for node in self.nodes.values():
            if not node.built:
                return False
        return True

    def build(self):
        nodes = self.get_buildable_targets()
        while nodes:
            nodes += self.build_target(nodes.pop())
        assert(self.is_build_complete())


    @staticmethod
    def _make_graph(targets):
        res = nx.DiGraph()
        res.add_nodes_from(targets)
        edges = []
        for target in targets:
            edges += [(depend, target) for depend in target.depends]
        res.add_edges_from(edges)
        return res