__author__ = 'Alexander Dethof'

from os.path import isdir
from metaConfig.metaTable import MetaTable


class MetaTree:

    def __init__(self, root_path):
        assert isinstance(root_path, basestring)
        assert isdir(root_path)

        self.__root_path = root_path
        self.__root_node = None

    def set_root_node(self, node):
        assert isinstance(node, MetaTable)
        self.__root_node = node

    def generate_files(self):
        if self.__root_node is None:
            return

        assert isinstance(self.__root_node, MetaTable)
        self.__root_node.generate_file(self.__root_path)
