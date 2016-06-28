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

    def _get_parser(self, src_path, stream_mode):
        """
        Returns an adequate bitstream parser concerning the currently used streaming settings.

        :param src_path: the path of the packet capture file to parse
        :type src_path: basestring

        :param stream_mode: the mode the data was streamed
        :type stream_mode: basestring

        :return: an adequate bitstream parser concerning the currently used streaming settings
        :rtype: bitstreamparse.bitStreamParser.BitStreamParser
        """

        assert isinstance(src_path, basestring)
        assert isinstance(stream_mode, basestring)
        assert stream_mode in self._hrc_table.VALID_STREAM_MODES

        if stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP:
            from bitstreamparse.udp.mp2t import Mp2t as UdpMp2t
            return UdpMp2t(src_path)

        elif stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP:
            from bitstreamparse.rtp.mp2t import Mp2t as RtpMp2t
            return RtpMp2t(src_path)

        elif stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_RAW_RTP:
            from bitstreamparse.rtp.rawVideo import RawVideo as RtpRawVideo
            return RtpRawVideo(src_path)

        else:
            raise Exception('Not implemented yet!')

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

        # set destination path
        destination_path = self._path \
                           + EXTRACT_DESTINATION_DIR \
                           + PATH_SEPARATOR \
                           + self._get_output_file_name(src_id, hrc_set, file_extension)

        hrc_id = hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID]

        if exists(destination_path) and not self._is_override_mode:
            print "# \033[95m\033[1mSKIP src %d : hrc %d\033[0m" % (src_id, hrc_id)
            return

        print "# \033[1m\033[94mRUN : [SRC:%d|HRC%d] scapy --> Extract payload from %s to %s\033[0m" % (
            src_id, hrc_id, src_path, destination_path
        )

        if self._is_dry_run:
            return

        parser = self._get_parser(src_path, stream_mode)

        # write bitstream into file
        payload_file = open(destination_path, 'w')
        payload_file.flush()

        bit_stream = parser.get_bit_stream()
        payload_file.write(bit_stream)

        payload_file.close()

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
