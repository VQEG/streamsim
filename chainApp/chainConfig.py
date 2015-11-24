__author__ = 'Alexander Dethof'

from filters.filterSet import FilterSet
# noinspection PyPep8Naming
from os.path import sep as PATH_SEPARATOR


class ChainConfig:

    def __init__(self):
        # tool specific config
        self.__tool_id = None
        self.__tool_options = dict()

        # run modes
        self.__is_log_mode = False
        self.__is_dry_run = False
        self.__is_override_mode = False
        self.__is_single_run = False
        self.__is_continuous_run = False

        self.__filters = None
        self.__path = '.'

    def set_filters(self, filters):
        """
        Parses a given list of filter strings which should apply to the application
        :param filters: the list filters to parse
            (scheme: ['filter_key1=filter_value1', 'filter_key2=filter_value2', ...])
        """

        assert isinstance(filters, list)
        self.__filters = FilterSet(filters)

    def get_filters(self):
        return self.__filters

    def set_tool_id(self, tool_id):
        assert isinstance(tool_id, basestring)
        self.__tool_id = tool_id

    def get_tool_id(self):
        return self.__tool_id

    def set_tool_options(self, options):
        assert isinstance(options, dict)
        self.__tool_options = options

    def get_tool_options(self):
        return self.__tool_options

    def set_log_mode(self, is_log_mode=True):
        assert isinstance(is_log_mode, bool)
        self.__is_log_mode = is_log_mode

    def is_log_mode(self):
        return self.__is_log_mode

    def set_dry_run(self, is_dry_run=True):
        assert isinstance(is_dry_run, bool)
        self.__is_dry_run = is_dry_run

    def is_dry_run(self):
        return self.__is_dry_run

    def set_override_mode(self, is_override_mode=True):
        assert isinstance(is_override_mode, bool)
        self.__is_override_mode = is_override_mode

    def is_override_mode(self):
        return self.__is_override_mode

    def set_single_run(self, is_single_run=True):
        assert isinstance(is_single_run, bool)
        self.__is_single_run = is_single_run

    def is_single_run(self):
        return self.__is_single_run

    def set_continuous_run(self, is_continuous_run=True):
        assert isinstance(is_continuous_run, bool)
        self.__is_continuous_run = is_continuous_run

    def is_continuous_run(self):
        return self.__is_continuous_run

    def set_path(self, path):
        assert isinstance(path, basestring)

        from os.path import isdir
        assert isdir(path), "The given path `%s` does not reference to a valid folder!" % path

        self.__path = path

    def get_path(self):
        return self.__path

    def get_log_folder_path(self):
        return self.__path + 'logs' + PATH_SEPARATOR

    def get_config_folder_path(self):
        return self.__path + 'config' + PATH_SEPARATOR