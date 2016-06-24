__author__ = 'Alexander Dethof'

from lossTool import LOSS_DESTINATION_DIR, LOSS_OUTPUT_FILE_TYPE_EXTENSION
from encodeTool import ENCODER_DESTINATION_DIR

ENCODED_SOURCE_DIR = ENCODER_DESTINATION_DIR
EXTRACT_SOURCE_DIR = LOSS_DESTINATION_DIR
EXTRACT_DESTINATION_DIR = 'outputPayload'

EXTRACT_MPEGTS_EXTENSION = 'ts'

TOOL_ID_EXTRACT = 'extract_payload'

# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR
from os.path import exists
from abstractTool import AbstractTool


class ExtractTool(AbstractTool):
    """
    This tool is used to extract the payload of the transmitted .pcap files.
    """

    def __validate_for_video_packet(self, packet, stream_mode):

        if stream_mode in self._hrc_table.SH_RTP_STREAM_MODES:
            uses_rtp = True
            from scapy.layers.rtp import RTP, Raw
        else:
            uses_rtp = False
            from scapy.layers.inet import UDP, Raw

        assert packet.haslayer(Raw), 'Packet does not contain any payload!'

        if uses_rtp:

            # noinspection PyUnboundLocalVariable
            pt = int(packet[RTP].getfieldval('payload'))

            # RTP-RAW
            if stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_RAW_RTP:
                assert 96 <= pt <= 127, 'Packet has no valid payload content! Content is: %s' % pt

            # RTP-MPEGTS
            elif stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP:
                assert pt == 33, 'Packet has no valid payload content! Content is: %s' % pt

        else:

            # UDP-MPEGTS
            if stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP:
                pass  # TODO is there a check required?

    def __dump_depacketization_state(self, src_id, hrc_id, packet_index, packet_count):
        """
        Dumps the depacketization state of a pcap file.

        :param src_id: the id of the source which is depacketized
        :type src_id: int

        :param hrc_id: the id of the applied HRC set
        :type hrc_id: int

        :param packet_index: the index of the packet which is opened
        :type packet_index: int

        :param packet_count: the number of total packets to depacketize
        :type packet_count: int
        """

        assert isinstance(src_id, int)
        assert isinstance(hrc_id, int)
        assert isinstance(packet_index, int)

        if packet_index > 1:
            self._remove_last_output()

        print '[SRC: %d|HRC: %d] Process packet: %d/%d' % (src_id, hrc_id, packet_index, packet_count)

    def __extract_payload(self, src_id, hrc_set, src_path, file_extension, stream_mode):
        """
        Writes the complete payload of a pcap file into a separate file.

        :param src_id: the id of the source the pcap file is linked to
        :type src_id: int

        :param hrc_set: the hrc set the pcap file is linked to
        :type hrc_set: dict

        :param src_path: the path of the pcap file to read
        :type src_path: basestring

        :param file_extension: The extension which is added to the file
        :type file_extension: basestring

        :param stream_mode: the mode how the data was streamed
        :type stream_mode: basestring
        """

        assert isinstance(src_id, int)
        assert isinstance(hrc_set, dict)
        assert isinstance(src_path, basestring)
        assert isinstance(file_extension, basestring)
        assert isinstance(stream_mode, basestring)
        assert stream_mode in self._hrc_table.VALID_STREAM_MODES

        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
        hrc_id = int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID])

        # create short handler if rtp streaming was used
        is_rtp = stream_mode in self._hrc_table.SH_RTP_STREAM_MODES

        # set destination folder
        destination_path = self._path \
                           + EXTRACT_DESTINATION_DIR \
                           + PATH_SEPARATOR \
                           + self._get_output_file_name(src_id, hrc_set, file_extension)

        if exists(destination_path) and not self._is_override_mode:
            print "# \033[95m\033[1mSKIP src %d : hrc %d\033[0m" % (src_id, hrc_id)
            return

        print "# \033[1m\033[94mRUN : SCAPY --> Extract payload from %s to %s\033[0m" % (src_path, destination_path)

        if self._is_dry_run:
            return

        # clear payload file
        payload_file = open(destination_path, 'w')
        payload_file.flush()
        payload_file.close()

        from scapy.all import Packet, rdpcap
        from scapy.all import bind_layers, split_layers
        from scapy.layers.inet import UDP

        if is_rtp:
            from scapy.layers.rtp import RTP, Raw
            bind_layers(UDP, RTP)
        else:
            from scapy.layers.inet import Raw
            bind_layers(UDP, Raw)

        captured_packets = rdpcap(src_path)
        payload_file = open(destination_path, 'ab')

        packet_count = len(captured_packets)
        packet_index = 1
        for packet in captured_packets:
            assert isinstance(packet, Packet)

            self.__dump_depacketization_state(src_id, hrc_id, packet_index, packet_count)

            try:
                self.__validate_for_video_packet(packet, stream_mode)
                payload_file.write(packet[Raw].load)
            except: pass

            packet_index += 1

        payload_file.close()

        # clean up layer binding for next payload extraction
        if is_rtp:
            # noinspection PyUnboundLocalVariable
            split_layers(UDP, RTP)
        else:
            from scapy.layers.inet import Raw
            split_layers(UDP, Raw)

    def __extract_source(self, src_id, hrc_set):
        """
        Extracts the payload from a streamed pcap source, given by its id, and the additional hrc configuration

        :param src_id: the id of the source to extract the payload of
        :type src_id: int

        :param hrc_set: a set of configurations applying on the extraction
        :type hrc_set: dict
        """

        assert isinstance(src_id, int)
        assert isinstance(hrc_set, dict)
        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
        assert self._hrc_table.DB_TABLE_FIELD_NAME_STREAM_MODE in hrc_set

        stream_mode = hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_STREAM_MODE]
        src_path = self._path + EXTRACT_SOURCE_DIR + PATH_SEPARATOR + self._get_output_file_name(
            src_id, hrc_set, LOSS_OUTPUT_FILE_TYPE_EXTENSION
        )

        # Recover the file extensions depending on the protocol packaging:
        # ----------------------------------------------------------------
        #
        # If the tool was not packed into a TS container, it still has the original
        # raw file extension

        if stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_RAW_RTP:
            codec = self._get_codec_by_hrc_set(hrc_set)
            file_extension = codec.get_raw_file_extension()

        # If the tool was packed into a TS container, the extension is .ts
        elif stream_mode in (
                self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP,
                self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP
        ):
            file_extension = EXTRACT_MPEGTS_EXTENSION

        # In all other cases there must be something wrong
        else:
            raise '[SRC%d|HRC%d] Invalid stream mode `%s` given!' % (
                src_id,
                hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID],
                stream_mode
            )

        # Besides from that we are now ready to extract the payload and store it in a given file format
        self.__extract_payload(
            src_id,
            hrc_set,
            src_path,
            file_extension,
            stream_mode
        )

    def __extract_source_with_hrc(self, source):
        """
        Extracts the payload of a given source in all its available HRC configurations.

        :param source: the source to extract the payload of
        :type source: dict
        """

        assert isinstance(source, dict)

        # get src id
        assert self._src_table.DB_TABLE_FIELD_NAME_SRC_ID in source
        src_id = int(source[self._src_table.DB_TABLE_FIELD_NAME_SRC_ID])

        # lookup all applying hrc settings and extract the payload
        #  of the source for these settings
        hrc_sets = self._pvs_matrix.get_hrc_sets_of_src_id(src_id)
        for hrc_set in hrc_sets:
            self.__extract_source(src_id, hrc_set)

    def execute(self):
        """
        Executes the tool, i.e. extracts the payload from all transmitted pcap files
        """

        super(self.__class__, self).execute()

        for src_set in self._src_sets:
            try:
                self.__extract_source_with_hrc(src_set)
            except KeyError or Warning, e:
                self._append_exception(e)

        self._show_we_summary()
