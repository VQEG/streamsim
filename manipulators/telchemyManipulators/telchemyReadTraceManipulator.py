__author__ = 'Alexander Dethof'

from manipulators.telchemyManipulators.abstractTelchemyManipulator import AbstractTelchemyManipulator
from manipulators.resources.telchemyManipulatorResource import TelchemyManipulatorReadTraceResource as TelchemyReadTraceRes
# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR
from os.path import isfile, exists
from cmd.command import Command

TRACES_FOLDER_NAME = 'traces'


class TelchemyReadTraceManipulator(AbstractTelchemyManipulator):
    """
    Class to represent a manipulator which focuses on the manipulation with telchemy and existing loss traces.
    """

    def __init__(self, parent, manipulator_settings_id, config_path):
        """
        Creates the manipulator for markov manipulation.

        :param parent: The parent which invoked the creation
        :type parent: manipulators.telchemyManipulator.TelchemyManipulator

        :param manipulator_settings_id: the id of the settings to manipulate for
        :type manipulator_settings_id: int

        :param config_path: the path where the config is located
        :type config_path: basestring
        """

        self.MANIPULATOR_RESOURCE_PATH = parent.MANIPULATOR_RESOURCE_PATH + PATH_SEPARATOR + 'read_trace'

        super(TelchemyReadTraceManipulator, self).__init__(parent, manipulator_settings_id, config_path)

    def _get_resource_handler(self):
        """
        Returns the resource handler

        :return: The resource handler
        :rtype: TelchemyReadTraceRes
        """

        return TelchemyReadTraceRes(self._config_path + self.MANIPULATOR_RESOURCE_PATH)

    def manipulate(self):
        """
        Performs the manipulation based on existing traces.
        """

        telchemy_command = Command(self._parent.MANIPULATOR_PROGRAM_PATH)
        trace_file_path = self._path \
                     + TRACES_FOLDER_NAME \
                     + PATH_SEPARATOR \
                     + self._settings[TelchemyReadTraceRes.DB_FIELD_NAME_TRACE_FILE_NAME]

        assert isfile(trace_file_path) and exists(trace_file_path), \
            "The specified trace file: `%s` is not a valid existing file!" % trace_file_path

        self._set_telchemy_command_file_input_output_options(telchemy_command)
        telchemy_command.set_as_posix_option('r', trace_file_path)

        # set loggings
        if self._log_folder and self._log_suffix:
            telchemy_log_file_path = self._get_log_file_path('telchemy')
            telchemy_command.set_as_log_file(telchemy_log_file_path)

        self._cmd(telchemy_command)
