__author__ = 'Alexander Dethof'

from abc import ABCMeta, abstractmethod
from manipulators.abstractManipulator import AbstractManipulator


class AbstractTelchemyManipulator(AbstractManipulator):

    __metaclass__ = ABCMeta

    def __init__(self, parent, manipulator_settings_id, config_path):
        super(AbstractTelchemyManipulator, self).__init__(parent, manipulator_settings_id, config_path)

    @abstractmethod
    def _get_resource_handler(self):
        pass

    @abstractmethod
    def manipulate(self):
        pass

    def _set_telchemy_command_file_input_output_options(self, telchemy_command):
        """
        Extends the given telchemy command with the source and destination file paths.

        :param telchemy_command: the command to modify
        :type telchemy_command: Command
        """

        telchemy_command.set_as_posix_option('i', self._src_file_path) \
                        .set_as_posix_option('o', self._dst_file_path)

