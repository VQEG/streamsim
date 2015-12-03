__author__ = 'Alexander Dethof'

from abc import ABCMeta, abstractmethod


class MetaConfigInterface(object):

    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def get_meta_description():
        pass
