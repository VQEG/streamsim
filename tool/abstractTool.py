__author__ = 'Alexander Dethof'

from abc import ABCMeta

from pvs import pvsMatrix
from chainApp.chainConfig import ChainConfig
from cmd.operator import Operator
from subtools.abstractSubTool import AbstractSubTool
from os.path import exists, isdir


class AbstractTool(Operator):
    """
    This class can be used as basic parent class for tools which are parts of the processing chain. It implements
    a field which stores the PVS matrix reference. Tools which are implemented with this base class should be
    executed by calling the public `execute` method.
    """

    # necessary to make this class abstract
    __metaclass__ = ABCMeta

    # true if catchable exceptions should be ignored during the process, else they will raise immediately
    _IGNORE_EXCEPTIONS_IN_PROCESS = True

    # true if the tool should show more detailed information
    _IS_INFO_MODE = False

    # true if warnings which are collected during the tool's process should be logged directly in the moment when they
    # occur
    _ALLOWS_WARNING_LOGS_DURING_PROCESS = True

    # true if exceptions which are collected during the tool's process should be logged directly in the moment when they
    # occur
    _ALLOWS_EXCEPTION_LOGS_DURING_PROCESS = True

    # true if the tool should give a brief summary about all warnings which have occurred during the tool's
    # initialization
    _ALLOWS_WARNING_SUMMARY = True

    # true if the tool should give a brief summary about all exceptions which have occurred during the tool's
    # initialization
    _ALLOWS_EXCEPTION_SUMMARY = True

    # Specification rules for valid options which can be set on the tool
    #
    # SCHEME:
    #
    # <OPTION_KEY>: <NR_OF_ARGUMENTS>
    _options_parser = dict()

    # specification of available sub tools
    _available_sub_tools = dict()

    def __init__(self, pvs_matrix, config):
        """
        Initializes the class with the given pvs matrix.
        :param pvs_matrix: the pvs matrix to initialize the object created by this class with
        """

        Operator.__init__(self)

        assert isinstance(config, ChainConfig)
        assert isinstance(pvs_matrix, pvsMatrix.PvsMatrix)
        assert isinstance(self._IS_INFO_MODE, bool)

        # connect pvs and config
        self._pvs_matrix = pvs_matrix
        self._config = config

        # set short handlers
        self._is_dry_run = self._config.is_dry_run()
        self._path = self._config.get_path()
        self._is_override_mode = config.is_override_mode()
        self._log_folder = None
        self._options = dict()

        # connect src
        self._src_table = self._pvs_matrix.get_src_table()
        self._src_sets = self._pvs_matrix.get_src_table().get_rows()

        # connect hrc
        self._hrc_table = self._pvs_matrix.get_hrc_table()

        self._warnings = list()
        self._exceptions = list()
        self._registered_sub_tools = list()

    def execute(self):
        """
        Function which should be overwritten in each tool, to execute the tool's functionality.
        """

    def _get_codec_by_hrc_set(self, hrc_set):
        """
        Returns the codec associated with a given HRC set, linked in its appropriate encoding settings!

        :param hrc_set: the hrc set to look up the codec for
        :type hrc_set: dict

        :return: codec associated with a given HRC set, linked in its appropriate encoding settings
        :rtype: coder.codec.abstractCodec.AbstractCodec
        """

        assert isinstance(hrc_set, dict)

        # get encoding table
        from pvs.hrc.encodingTable import EncodingTable
        encoding_table = self._hrc_table.get_encoding_table()

        # get encoding set for id
        assert EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID in hrc_set
        encoding_id = hrc_set[EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID]
        encoding_set = encoding_table.get_row_with_id(encoding_id)

        # get codec id and codec settings id
        assert EncodingTable.DB_TABLE_FIELD_NAME_CODEC_ID in encoding_set
        codec_id = encoding_set[EncodingTable.DB_TABLE_FIELD_NAME_CODEC_ID]

        assert EncodingTable.DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID in encoding_set
        codec_settings_id = encoding_set[EncodingTable.DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID]

        # return the associated codec
        from coder.codec.codecList import get_codec
        return get_codec(codec_id, codec_settings_id, self._config.get_config_folder_path())

    def _get_codec_by_hrc_id(self, hrc_id):
        """
        Returns the codec associated with a given HRC id, linked in its appropriate encoding settings!

        :param hrc_id: the hrc id to look up the appropriate codec for
        :type hrc_id: int

        :return: codec associated with a given HRC id, linked in its appropriate encoding settings
        :rtype: coder.codec.abstractCodec.AbstractCodec
        """

        assert isinstance(hrc_id, int)

        # get hrc set for given id and return codec for
        hrc_set = self._hrc_table.get_row_with_id(hrc_id)
        return self._get_codec_by_hrc_set(hrc_set)


    @staticmethod
    def _switch_file_extension(file_name, extension):
        """
        Changes the file extension of a given file name

        :param file_name: the full file name to change the extension of
        :type file_name: basestring

        :param extension: the extension to change to
        :type extension: basestring

        :return: the new file name with the new extension
        :rtype: str
        """

        assert isinstance(file_name, basestring)
        assert isinstance(extension, basestring)

        from os.path import splitext
        from os import extsep

        path, old_extension = splitext(file_name)

        return '%s%s%s' % (path, extsep, extension)

    def _cleanup_sub_tools(self):
        """
        Calls the cleanup function in each sub tool
        """

        for sub_tool in self._registered_sub_tools:
            sub_tool.cleanup()

    def _get_output_dir_name(self, src_id, hrc_set):
        """
        Returns the name of the folder where to put out some results.

        :param src_id: the source id for which results have to be put into a folder
        :type src_id: int

        :param hrc_set: the hrc set for which results have to be put into the folder
        :type hrc_set: dict

        :return: The name of the folder where to put out some results
        :rtype: str
        """

        assert self._src_table.has_row_with_id(src_id)
        assert isinstance(hrc_set, dict)

        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
        hrc_id = int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID])

        return 'SRC%d_HRC%d' % (src_id, hrc_id)

    def _get_output_file_name(self, src_id, hrc_set, file_type_extension=None):
        """
        Returns the name of the output file for a given source, its settings and a given file extension

        :param src_id: the id of the source
        :type src_id: int

        :param hrc_set: the settings for the source
        :type hrc_set: dict

        :param file_type_extension: the file type extension of the output type
        :type file_type_extension: basestring

        :return: the name of the output file for a given source, its settings and a given file extension
        :rtype: str
        """

        dir_name = self._get_output_dir_name(src_id, hrc_set)

        if isinstance(file_type_extension, basestring):
            from os import extsep
            return '%s%s%s' % (dir_name, extsep, file_type_extension)
        else:
            return dir_name

    def _append_exception(self, e):
        """
        Adds an exception to the tool's exceptions collection. It differs between warnings and all other exceptions.
        In further progresses the warnings and exceptions can be requested to be displayed in a brief summary. If the
        tool is allowed to it displays the warnings and exceptions directly in the moment when they occur.

        :param e: the exception to append
        :type e: Exception
        """

        if not self._IGNORE_EXCEPTIONS_IN_PROCESS:
            raise e

        if isinstance(e, Warning):
            self._warnings.append(e)
            if self._ALLOWS_WARNING_LOGS_DURING_PROCESS:
                self._log_warning(e)

        else:
            self._exceptions.append(e)
            if self._ALLOWS_EXCEPTION_LOGS_DURING_PROCESS:
                self._log_exception(e)

    def _show_we_summary(self):
        """
        Prints a brief summary about the warnings and all other exceptions which have been collected by the tool. The
        summary can be filtered by the exception type (warning/exception).
        """

        if self._ALLOWS_WARNING_SUMMARY and self._warnings:
            warning_count_report_text = '%d warnings occurred!' % len(self._warnings)
            print '\n%s\n%s' % (warning_count_report_text, len(warning_count_report_text) * '-')
            for warning in self._warnings:
                self._log_warning(warning)

        if self._ALLOWS_EXCEPTION_SUMMARY and self._exceptions:
            exceptions_count_report_text = '%d exceptions occurred!' % len(self._exceptions)
            print '\n%s\n%s' % (exceptions_count_report_text, len(exceptions_count_report_text) * '-')
            for exception in self._exceptions:
                self._log_exception(exception)

    def _import_sub_tool(self, tool_id):
        """
        Imports a sub tool and registers it in the tool's sub-tool chain. Has to be overridden individually for each
        tool which makes us of sub tools.

        :param tool_id: the id of the sub tool to load
        :type tool_id: basestring

        :return: the sub tool
        :rtype: AbstractSubTool

        :raises: KeyError on default, if this method is not overridden!
        """

        assert isinstance(tool_id, basestring)
        raise KeyError("The tool `%s` does not support to load the sub-tool: `%s`" % (self.__class__.__name__, tool_id))

    def set_tool_options(self, options):
        """
        Sets tool-specific options.

        :param options: the tool-specific options to set
        :type options: dict[]
        """

        tool_name = self.__class__.__name__
        for opt_item in options:
            assert isinstance(opt_item, basestring)
            opt_item_spec = opt_item.split('=')

            assert isinstance(opt_item_spec, list)
            opt_item_len = len(opt_item_spec)
            assert 1 <= opt_item_len <= 2

            opt_key = opt_item_spec[0]

            if opt_key not in self._options_parser:
                raise SyntaxError(
                    'Invalid option `%s` given to the tool `%s`!' % (opt_key, tool_name)
                )

            if opt_key in self._options:
                raise AttributeError("Option `%s` is already defined in the options of the tool `%s`!" % (
                                     opt_key, tool_name
                                     )
                )

            nr_arguments = self._options_parser[opt_key]
            if (nr_arguments == 0 and opt_item_len > 1) or (opt_item_len == 1 and nr_arguments > 0):
                raise SyntaxError(
                    "The tool `%s` received a wrong option input for `%s`. This option requires %d arguments, but only "
                    "%d were given!" % (tool_name, opt_key, nr_arguments, opt_item_len - 1)
                )

            if nr_arguments:
                opt_args = opt_item_spec[1].split(',')
                opt_args_count = len(opt_args)
                assert opt_args_count == nr_arguments, "Option `%s` (tool: `%s`) received the wrong number of arguments " \
                                                       "(%d). Required: %d." % (
                                                           opt_key, tool_name, opt_args_count, nr_arguments
                                                       )
            else:
                opt_args = True

            self._options[opt_key] = opt_args

    def set_log_folder(self, log_folder_path):
        assert isinstance(log_folder_path, basestring)
        assert isdir(log_folder_path)

        self._log_folder = log_folder_path

    def cleanup(self):
        """
        Can be overridden to execute clean up processes, when the tool is exit.
        """

        self._cleanup_sub_tools()

    def request_sub_tool(self, tool_id):
        """
        Requests the tool to load a sub tool and to register it in it's sub tool queue.

        :param tool_id: the id of the tool to load
        :type tool_id: basestring

        :return: the tool to load
        :rtype: AbstractSubTool

        :raises: KeyError, if the requested tool is not available
        """

        assert isinstance(tool_id, basestring)

        if tool_id is self._available_sub_tools:
            return self._import_sub_tool(tool_id)

        raise KeyError('The requested sub tool `%s` does not exist!' % tool_id)

    def _register_sub_tool(self, sub_tool):
        """
        Registers a sub tool in the tool's sub tool list

        :param sub_tool: the tool to register
        :type sub_tool: AbstractSubTool
        """

        assert isinstance(sub_tool, AbstractSubTool)
        self._registered_sub_tools.append(sub_tool)

    def _unregister_sub_tool(self, sub_tool):
        """
        Unregisters a sub tool from the tool's sub tool list

        :param sub_tool: the tool to unregister
        :type sub_tool: AbstractSubTool
        """

        assert isinstance(sub_tool, AbstractSubTool)

        if sub_tool in self._registered_sub_tools:
            sub_tool.cleanup()
            self._registered_sub_tools.remove(sub_tool)
        else:
            raise RuntimeError("Tool `%s` can not unregister the tool,"
                               " because it is not part of the tool's registered ones!")


