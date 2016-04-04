__author__ = 'Alexander Dethof'

from abc import ABCMeta, abstractmethod
from os.path import isfile, exists, isdir

from cmd.operator import Operator
from tool.abstractTool import AbstractTool


class AbstractManipulator(Operator):
    """
    Abstract class representing a manipulator which can be used to manipulate a captured packet stream in order to
    insert packet loss.
    """

    __metaclass__ = ABCMeta

    def __init__(self, parent, manipulator_settings_id, config_path):
        """
        Initializes the manipulator for a parent based on a specific manipulator settings id.

        :param parent: The parent to load the manipulator for
        :type parent: AbstractTool|AbstractManipulator

        :param manipulator_settings_id: the id of the manipulation
        :type manipulator_settings_id: int

        :param config_path: the path where the config is located
        :type config_path: basestring
        """

        super(AbstractManipulator, self).__init__()

        assert isinstance(parent, AbstractManipulator) or isinstance(parent, AbstractTool)
        assert isinstance(manipulator_settings_id, int)
        assert isinstance(config_path, basestring)
        assert isdir(config_path) and exists(config_path)

        self._path = ''
        self._src_file_path = ''
        self._dst_file_path = ''
        self._log_folder = ''
        self._log_suffix = ''
        self._parent = parent
        self._config_path = config_path

        self._is_loss_trace_enabled = False
        self._is_trace_only = False
        self._is_override_mode = False

        self._load_manipulator_settings_for_id(manipulator_settings_id)

    @abstractmethod
    def _get_resource_handler(self):
        """
        Returns a handler for the resource file wherein the manipulation is specified.

        :return: A  handler for the resource file wherein the manipulation is specified
        :rtype: database.dbHandler.DbHandler
        """

        pass

    @abstractmethod
    def manipulate(self):
        """
        Performs the main manipulation.
        """

        pass

    def _get_trace_file_path(self):
        """
        Returns the path where the loss trace is dumped in.

        :return: The path where the loss trace is dumped in
        :rtype: str
        """

        # noinspection PyPep8Naming
        from os.path import splitext, extsep as FILE_EXTENSION_SEPARATOR

        # build path where to export the loss trace
        trace_file_path = splitext(self._dst_file_path)
        assert len(trace_file_path) == 2

        trace_file_path = trace_file_path[0]
        trace_file_path += FILE_EXTENSION_SEPARATOR + 'csv'

        return trace_file_path

    def _get_log_file_path(self, log_prefix):
        """
        Returns the path where the manipulation log output is dumped to.

        :param log_prefix: the prefix which is appended to the log file.
        :type log_prefix: basestring

        :return: The path where the manipulation log output is dumped to
        :rtype: str
        """

        assert isinstance(log_prefix, basestring)

        # noinspection PyPep8Naming
        from os import sep as PATH_SEPARATOR

        return self._log_folder + PATH_SEPARATOR + log_prefix + '_' + self._log_suffix

    def _load_manipulator_settings_for_id(self, manipulator_settings_id):
        """
        Loads the manipulator settings of the appropriate manipulator resource table.

        :param manipulator_settings_id: id of the setting to load
        :type manipulator_settings_id: int
        """

        resource_table = self._get_resource_handler()
        settings = resource_table.get_row_with_id(manipulator_settings_id)

        self._settings = settings

    def set_path(self, path):
        """
        Sets the general path prefix

        :param path: The general path prefix
        :type path: str

        :return: self
        :rtype: AbstractManipulator
        """

        assert isinstance(path, basestring)
        self._path = path

        return self

    def set_log_settings(self, log_folder, log_suffix):
        """
        Sets the log settings.

        :param log_folder: The folder where to log the output to.
        :type log_folder: basestring

        :param log_suffix: the suffix of the file to log the output in.
        :type log_suffix: basestring

        :return: self
        :rtype: AbstractManipulator
        """

        assert isinstance(log_folder, basestring) or log_folder is None
        assert isinstance(log_suffix, basestring)

        if log_folder:
            assert isdir(log_folder)
            assert exists(log_folder)

        self._log_folder = log_folder
        self._log_suffix = log_suffix

        return self

    def set_trace_only_state(self, is_trace_only=True):
        """
        Sets, that the manipulator should only trace the loss and not manipulate (if possible).

        :param is_trace_only: True if the manipulator should only trace the loss and not manipulate (if possible),
            false otherwise.
        :type is_trace_only: bool

        :return: self
        :rtype: AbstractManipulator
        """

        assert isinstance(is_trace_only, bool)

        self._is_trace_only = is_trace_only
        return self

    def set_loss_trace_enabled(self, is_enabled=True):
        """
        Sets, if it is allowed to generate a loss trace during the manipulation (if possible)

        :param is_enabled: True if it is allowed to generate a loss trace during the manipulation (if possible),
            false otherwise.
        :type is_enabled: bool

        :return: self
        :rtype: AbstractManipulator
        """

        assert isinstance(is_enabled, bool)

        self._is_loss_trace_enabled = is_enabled
        return self

    def set_src_file(self, src_file_path):
        """
        Sets the path of the file where a packet capture is extracted and manipulated.

        :param src_file_path: file path of the file to read and to manipulate
        :type src_file_path: basestring

        :return: self
        :rtype: AbstractManipulator
        """

        assert isinstance(src_file_path, basestring)
        assert isfile(src_file_path)

        self._src_file_path = src_file_path
        return self

    def set_dst_file(self, dst_file_path):
        """
        Sets the destination file path where to pack the manipulated packet capture.

        :param dst_file_path: file path where to pack the manipulated packet capture
        :type dst_file_path: basestring

        :return: self
        :rtype: AbstractManipulator
        """

        assert isinstance(dst_file_path, basestring)

        self._dst_file_path = dst_file_path
        return self

    def set_override_mode(self, is_override):
        """
        Sets if the override mode is enabled.

        :param is_override: True if the override mode is enabled, false otherwise.
        :type is_override: bool

        :return: self
        :rtype: AbstractManipulator
        """

        assert isinstance(is_override, bool)

        self._is_override_mode = is_override
        return self

    def cleanup(self):
        """
        Function called on exit of the application - Enables the possibility to clean up several stuff before the
        application will exit completely
        """

        pass