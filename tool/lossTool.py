__author__ = 'Alexander Dethof'

from streamTool import STREAM_DESTINATION_DIR
LOSS_SOURCE_DIR = STREAM_DESTINATION_DIR
LOSS_DESTINATION_DIR = 'outputPcapLoss'
LOSS_OUTPUT_FILE_TYPE_EXTENSION = 'pcap'

TOOL_ID_LOSS = 'insert_loss'

from abstractTool import AbstractTool
from streamTool import STREAM_OUTPUT_FILE_TYPE_EXTENSION
from pvs.hrc.packetLossTable import PacketLossTable
# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR, remove
from os.path import isfile, exists
from manipulators.abstractManipulator import AbstractManipulator
from subtools.abstractSubTool import AbstractSubTool
from subtools.lossTraceParser import LossTraceParser


class LossTool(AbstractTool):
    """
    This tool is used to re-stream a collection of pcap files in error prone networks with packet loss. The resulting
    pcap files will be stored in a separate file.
    """

    # define the available manipulators of the loss tool
    LOSS_TOOL_TC = 'tc'
    LOSS_TOOL_TELCHEMY = 'telchemy'
    LOSS_TOOL_NONE = 'none'

    # define the available tool options
    OPTION_STORE_LOSS_TRACES = 'store_loss_traces'
    OPTION_TRACE_ONLY = 'trace_only'

    _options_parser = {
        # if option store_loss_traces is set -> the loss traces will be stored; if not set -> no trace will be stored!
        OPTION_STORE_LOSS_TRACES: 0,

        # if option trace_only is set -> only the loss traces will be done
        OPTION_TRACE_ONLY: 0
    }

    # configure available sub tools
    SUB_TOOL_TRACE_PARSER = 'trace_parser'

    _available_sub_tools = (
        SUB_TOOL_TRACE_PARSER
    )

    def __init__(self, pvs_matrix, config):
        """
        Initialization of the loss insertion tool with the PVS matrix, which returns information about the network
        loss settings.
        :param pvs_matrix: the pvs matrix, describing the loss settings
        :param config: the config used for the tool's execution
        """
        super(self.__class__, self).__init__(pvs_matrix, config)

        self.__packet_loss_table = pvs_matrix.get_hrc_table().get_packet_loss_table()
        assert isinstance(self.__packet_loss_table, PacketLossTable)

        self.__manipulator = None

    def _import_sub_tool(self, tool_id):
        """
        Imports a sub tool registered with the given tool id.

        :param tool_id: the id of the sub tool to load
        :type tool_id: basestring

        :return: the requested sub tool
        :rtype: AbstractSubTool
        """

        assert isinstance(tool_id, basestring)

        sub_tool = None
        if tool_id == self.SUB_TOOL_TRACE_PARSER:
            from subtools.lossTraceParser import LossTraceParser
            sub_tool = LossTraceParser(self)

        # further sub tools can be added here with "elif"-commands!

        if isinstance(sub_tool, AbstractSubTool):
            self._register_sub_tool(sub_tool)
            return sub_tool

        raise KeyError('There exists no equivalent sub-tool representation for the sub-tool id `%s`' % tool_id)

    def __get_manipulator(self, packet_loss_settings):
        """
        Returns a packet manipulator which can be used by the tool to insert loss and other behaviour of
        error-prone networks into the captured pcap files from the streaming tool.

        :param packet_loss_settings: the settings defining the state of the packet loss
        :type packet_loss_settings: dict

        :return: a packet manipulator which can be used by the tool to insert loss and other behaviour of
        error-prone networks into the captured pcap files from the streaming tool
        :rtype: AbstractManipulator
        """

        # TODO extract method into manipulators package

        assert isinstance(packet_loss_settings, dict)
        assert PacketLossTable.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL in packet_loss_settings

        manipulator_id = packet_loss_settings[PacketLossTable.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL]
        if manipulator_id == self.LOSS_TOOL_NONE:
            return None

        assert PacketLossTable.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL_ID in packet_loss_settings
        manipulator_settings_id = int(packet_loss_settings[PacketLossTable.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL_ID])

        if manipulator_id == self.LOSS_TOOL_TC:
            from manipulators.trafficControlManipulator import TrafficControlManipulator
            return TrafficControlManipulator(self, manipulator_settings_id, self._config.get_config_folder_path())

        if manipulator_id == self.LOSS_TOOL_TELCHEMY:
            from manipulators.telchemyManipulator import TelchemyManipulator
            return TelchemyManipulator(self, manipulator_settings_id, self._config.get_config_folder_path())

        """
        Further manipulators can be added here in the following scheme:

        if manipulator_id == <MANIPULATOR_ID>:
            from manipulators.<manipulatorId> import <ManipulatorId>Manipulator
            return <ManipulatorId>Manipulator(manipulator_settings_id)
        """

        raise KeyError('Could not find a packet manipulator with name `%s`' % manipulator_id)

    def __insert_loss_in_source_by_hrc(self, src_id, hrc_set):
        """
        Re-streams a source according to the given network settings.

        :param src_id: the id of the source to manipulate
        :type src_id: int

        :param hrc_set: the settings which direct the manipulation
        :type hrc_set: dict
        """

        src_path = self._path + LOSS_SOURCE_DIR + PATH_SEPARATOR + self._get_output_file_name(
            src_id, hrc_set, STREAM_OUTPUT_FILE_TYPE_EXTENSION
        )

        if not isfile(src_path):
            raise Warning(
                'No loss can be inserted in source %s, since there could not be found an appropriate file for.'
                % src_path
            )

        destination_path = self._path + LOSS_DESTINATION_DIR + PATH_SEPARATOR + self._get_output_file_name(
            src_id, hrc_set, LOSS_OUTPUT_FILE_TYPE_EXTENSION
        )

        # check if the destination path already exists -> check override mode to skip or to override
        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
        hrc_id = int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID])

        if exists(destination_path):
            if self.OPTION_TRACE_ONLY in self._options:
                print "# \033[95m\033[1mTRACE ONLY src %d : hrc %d\033[0m"\
                      % (src_id, hrc_id)
            else:
                if self._is_override_mode:
                    if not self._is_dry_run:
                        remove(destination_path)
                    print "# \033[95m\033[1mREMOVE src %d : hrc %d\033[0m"\
                          % (src_id, hrc_id)
                else:
                    print "# \033[95m\033[1mSKIP src %d : hrc %d\033[0m"\
                          % (src_id, hrc_id)
                    return

        packet_loss_id = int(hrc_set[PacketLossTable.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID])
        packet_loss_settings = self.__packet_loss_table.get_row_with_id(packet_loss_id)

        is_loss_trace_mode = self.OPTION_STORE_LOSS_TRACES in self._options
        is_trace_only_mode = self.OPTION_TRACE_ONLY in self._options

        if is_trace_only_mode:
            self.__trace_loss(src_path, destination_path)
            return

        self.__manipulator = self.__get_manipulator(packet_loss_settings)

        if self.__manipulator is None:
            # if no loss is specified -> just copy!
            print '# [SRC_ID: %d|HRC_ID: %d] \033[95m\033[1mNO LOSS CASE: Just Copy!\033[0m' % (src_id, hrc_id)
            if not self._is_dry_run:
                from shutil import copyfile
                copyfile(src_path, destination_path)
            return

        self.__manipulator.set_src_file(src_path) \
            .set_dst_file(destination_path) \
            .set_path(self._path) \
            .set_override_mode(self._is_override_mode) \
            .set_loss_trace_enabled(self.OPTION_STORE_LOSS_TRACES in self._options) \
            .set_trace_only_state(self.OPTION_TRACE_ONLY in self._options) \
            .set_override_mode(self._is_override_mode) \
            .set_dry_mode(self._is_dry_run) \
            .set_log_settings(
                self._log_folder,
                self._get_output_file_name(src_id, hrc_set, 'log')
            ) \
            .manipulate()

        if is_loss_trace_mode:
            self.__trace_loss(src_path, destination_path)

    def __trace_loss(self, complete_pcap_file_path, lossy_pcap_file_path):
        """
        Compares a complete pcap file with a lossy one and stores the loss trace in a separate CSV file.

        :param complete_pcap_file_path: the file which consists of all packets
        :type complete_pcap_file_path: basestring

        :param lossy_pcap_file_path: the file which consists of the residual (i.e. "unlost") packets
        :type lossy_pcap_file_path: basestring
        """

        assert isinstance(complete_pcap_file_path, basestring)
        assert isinstance(lossy_pcap_file_path, basestring)

        if self._is_dry_run:
            print "# \033[95m\033[1m[TRACE] not traceable due to dry mode!\033[0m"
            return

        trace_file_path = self._switch_file_extension(complete_pcap_file_path, 'csv')

        if exists(trace_file_path) and not self._is_override_mode:
            from os.path import basename
            print "# \033[95m\033[1m[TRACE] SKIP %s\033[0m" % basename(trace_file_path)
            return

        parser = self.request_sub_tool(self.SUB_TOOL_TRACE_PARSER)
        assert isinstance(parser, LossTraceParser)

        parser.set_complete_file_path(complete_pcap_file_path) \
              .set_loss_file_path(lossy_pcap_file_path) \
              .set_trace_file_path(trace_file_path) \
              .trace()

    def __insert_loss_in_source(self, src_id):
        """
        Inserts loss for a single given source according to all applicable HRC variation linked to this source

        :param src_id: the id of the source to manipulate
        :type src_id: int
        """

        assert isinstance(src_id, int)

        hrc_sets = self._pvs_matrix.get_hrc_sets_of_src_id(src_id)

        for hrc_set in hrc_sets:
            # try:
            self.__insert_loss_in_source_by_hrc(src_id, hrc_set)
            # except Warning as w:
            #     self._log_warning(w)
            # except (KeyError, AssertionError) as e:
            #     self._log_exception(e)

    def cleanup(self):
        """
        Cleans up the tool with all it's sub tools and manipulators
        """

        super(LossTool, self).cleanup()

        if isinstance(self.__manipulator, AbstractManipulator):
            self.__manipulator.cleanup()

    def execute(self):
        """
        Goes through all stored pcap files in the source dir and manipulates the network traffic according to the
        settings made in the HRC table. Then the tool re-streams the files and stores the residual captured packets in
        a further pcap file.
        """

        super(self.__class__, self).execute()

        for src_set in self._src_sets:
            src_id = int(src_set[self._src_table.DB_TABLE_FIELD_NAME_SRC_ID])
            self.__insert_loss_in_source(src_id)

        self._show_we_summary()
