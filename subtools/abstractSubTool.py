__author__ = 'Alexander Dethof'


from abc import ABCMeta
from cmd.operator import Operator


class AbstractSubTool(Operator):
    """
    Implements an abstract base class used to generate new sub tools.
    """

    __metaclass__ = ABCMeta

    def __init__(self, parent):
        """
        Sets up the sub tool and links it with its parent.

        :param parent: The tool to which this sub tool belongs
        :type parent: tool.abstractTool.AbstractTool
        """

        super(AbstractSubTool, self).__init__()

        # subtools can be only created by tools!
        # TODO assert isinstance(parent, AbstractTool)

        self._parent = parent

    def cleanup(self):
        """
        Cleans up the sub tool (has to be called on exit)
        """

        pass