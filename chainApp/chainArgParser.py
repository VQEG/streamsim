__author__ = 'Alexander Dethof'

from chainApp.chainToolRunner import ChainToolRunner
from chainArgs import ChainArgs
from chainConfig import ChainConfig
# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR


class ChainArgParser:

    CHAIN_ARGUMENT_PARSER_DESCRIPTION = "HEVC processing chain for subjective evaluation in error prone networks"

    def __init__(self, config):
        """

        :return:
        """

        assert isinstance(config, ChainConfig)

        arg_parser = ChainArgs(self.CHAIN_ARGUMENT_PARSER_DESCRIPTION)
        self.__arguments = arg_parser.parse()

        self.__config = config

    def reset_configuration(self):
        """

        :return:
        """

        # configure tool id
        assert hasattr(self.__arguments, 'tool_id')
        self.__config.set_tool_id(self.__arguments.tool_id)

        # configure dry run
        assert hasattr(self.__arguments, 'is_dry_run')
        self.__config.set_dry_run(self.__arguments.is_dry_run)

        # configure single run
        assert hasattr(self.__arguments, 'is_single_run')
        self.__config.set_single_run(self.__arguments.is_single_run)

        # configure continuous mode
        assert hasattr(self.__arguments, 'is_continuous_run')
        self.__config.set_continuous_run(self.__arguments.is_continuous_run)

        # configure override mode
        assert hasattr(self.__arguments, 'is_override_mode')
        self.__config.set_override_mode(self.__arguments.is_override_mode)

        # configure log mode
        assert hasattr(self.__arguments, 'is_log_mode')
        self.__config.set_log_mode(self.__arguments.is_log_mode)

        # configure execution path
        assert hasattr(self.__arguments, 'path')
        if self.__arguments.path[len(self.__arguments.path) - 1] == PATH_SEPARATOR:
            self.__config.set_path(self.__arguments.path)
        else:
            self.__config.set_path(self.__arguments.path + PATH_SEPARATOR)

        # configure filters
        assert hasattr(self.__arguments, 'filters')
        self.__config.set_filters(self.__arguments.filters)

        # configure tool options
        tool_options = dict()
        for tool_id in ChainToolRunner.TOOL_EXECUTION_ORDER:
            assert hasattr(self.__arguments, '%s_options' % tool_id)
            tool_options[tool_id] = getattr(self.__arguments, '%s_options' % tool_id)

        self.__config.set_tool_options(tool_options)
