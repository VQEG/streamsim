__author__ = 'Alexander Dethof'

from argparse import ArgumentParser
from chainToolRunner import ChainToolRunner

from tool.encodeTool import TOOL_ID_ENCODE
from tool.streamTool import TOOL_ID_STREAM
from tool.lossTool import TOOL_ID_LOSS
from tool.extractTool import TOOL_ID_EXTRACT
from tool.decodeTool import TOOL_ID_DECODE


class ChainArgs():

    # link tools with short names
    __short_name_dict = {
        TOOL_ID_ENCODE: ChainToolRunner.SHORT_ID_ENCODE,
        TOOL_ID_STREAM: ChainToolRunner.SHORT_ID_STREAM,
        TOOL_ID_LOSS: ChainToolRunner.SHORT_ID_LOSS,
        TOOL_ID_EXTRACT: ChainToolRunner.SHORT_ID_EXTRACT,
        TOOL_ID_DECODE: ChainToolRunner.SHORT_ID_DECODE
    }

    def __init__(self, argument_parser_description):
        """

        :param argument_parser_description:
        :return:
        """

        self.__arg_parser = ArgumentParser(argument_parser_description)

        self.__add_tool_id_argument() \
            .__add_single_run_opt() \
            .__add_dry_run_opt() \
            .__add_continuous_run_opt() \
            .__add_override_mode_opt() \
            .__add_log_opt() \
            .__add_path_opt() \
            .__add_tool_options() \
            .__add_filter_opt()

    def __add_bool_flag(self, name, short_name, destination, metavarname, helptext):
        """

        :param name:
        :param short_name:
        :param destination:
        :param metavarname:
        :param helptext:
        :return:
        """

        self.__arg_parser.add_argument(
            '-%s' % short_name,
            '--%s' % name,
            dest=destination,
            metavar=metavarname,
            type=bool,
            const=True,
            default=False,
            nargs='?',
            help=helptext
        )

    def __add_tool_id_argument(self):
        """

        :return:
        """

        self.__arg_parser.add_argument(
            'tool_id',
            type=str,
            choices=[
                TOOL_ID_ENCODE,
                TOOL_ID_STREAM,
                TOOL_ID_LOSS,
                TOOL_ID_EXTRACT,
                TOOL_ID_DECODE,
                ChainToolRunner.TOOL_ID_RUN_ALL,
                ChainToolRunner.TOOL_ID_CLEAN_UP,
                ChainToolRunner.TOOL_ID_SETUP
            ],
            default=ChainToolRunner.TOOL_ID_RUN_ALL,
            nargs='?',
            help='Name of the (last) tool to execute in the processing chain. '
                 'If this option is not set all steps in the chain will be executed.\n\n'
                 'NOTE: The `cleanup` command will not execute a tool, but will try to revert all changes which might '
                 'have affected the system by previous executions. All other parameters will be ignored with this'
                 ' command!'
        )

        return self

    def __add_single_run_opt(self):
        """

        :return:
        """

        self.__add_bool_flag(
            'single_run',
            's',
            'is_single_run',
            'RUN_AS_SINGLE_STEP',
            'Set this flag if the chain should only execute the process with the given id. Otherwise all processes '
            'before and the tool given at the process id will be executed.'
        )

        return self

    def __add_dry_run_opt(self):
        """

        :return:
        """

        self.__add_bool_flag(
            'dry_run',
            'd',
            'is_dry_run',
            'RUN_IN_DRY_MODE',
            'Set this flag if the tool should be run dry.'
        )

        return self

    def __add_continuous_run_opt(self):
        """

        :return:
        """

        self.__add_bool_flag(
            'cont',
            'c',
            'is_continuous_run',
            'RUN_TILL_END_OF_CHAIN',
            'Set this flag if the chain should start at the given tool and run from there the residual chain.'
        )

        return self

    def __add_log_opt(self):
        """

        :return:
        """

        self.__add_bool_flag(
            'log',
            'l',
            'is_log_mode',
            'IS_LOG_MODE',
            'Set this flag, if all sub applications started by the processing chain should log their outputs in a pre-'
            'specified log-folder. If this flag is not set their outputs will be dumped to STDOUT.'
        )

        return self

    def __add_override_mode_opt(self):
        """

        :return:
        """

        self.__add_bool_flag(
            'override',
            'y',
            'is_override_mode',
            'OVERRIDE_FILES',
            'Set this flag if the chain should override all processed files; if not set, the chain will skip '
            'already created files.'
        )

        return self

    def __add_path_opt(self):
        """

        :return:
        """

        self.__arg_parser.add_argument(
            '-p',
            '--path',
            dest='path',
            type=str,
            default='.',
            const='.',
            nargs='?',
            help='Sets the path where to execute the chain operations in. And where to print the logging (if enabled).'
        )

        return self

    def __add_tool_options(self):
        """

        :return:
        """

        short_name_items = self.__short_name_dict.items()
        for (tool_id, short_id) in short_name_items:
            assert isinstance(short_id, basestring)
            assert isinstance(tool_id, basestring)

            self.__arg_parser.add_argument(
                '-to:%s' % short_id,
                '--tool_options:%s' % tool_id,
                dest='%s_options' % tool_id,
                metavar='OPTIONS_FOR_TOOL_%s' % tool_id.upper(),
                type=str,
                default={},
                nargs='+',
                help='Sets options for the `%s`-tool. Further documentation about this can be found in the wiki.'
                     % tool_id
            )

        return self

    def __add_filter_opt(self):
        """

        :return:
        """

        self.__arg_parser.add_argument(
            '-f',
            '--filter',
            dest='filters',
            metavar='FILTER_ARGUMENTS',
            type=str,
            default=[],
            nargs='+',
            help='Sets some additional filters, e.g. for the processing sources'
        )

        return self

    def parse(self):
        """

        :return:
        """

        return self.__arg_parser.parse_args()