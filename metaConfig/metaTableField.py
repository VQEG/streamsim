__author__ = 'Alexander Dethof'


class MetaTableField:

    def __init__(self, name, type, doc='', variants=list()):
        self.__name = name
        self.__type = type
        self.__doc = doc
        self.__variants = variants

    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__type

    def get_doc(self):
        return self.__doc

    def get_variants(self):
        return self.__variants
