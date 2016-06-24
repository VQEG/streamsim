__author__ = 'Alexander Dethof'

from extractTool import EXTRACT_DESTINATION_DIR, EXTRACT_MPEGTS_EXTENSION
DECODER_SOURCE_DIR = EXTRACT_DESTINATION_DIR
DECODER_DESTINATION_DIR = 'outputDecoded'
DECODE_OUTPUT_FILE_TYPE_EXTENSION = 'avi'

TOOL_ID_DECODE = 'decode_loss'

from abstractTool import AbstractTool
from coder.coderList import get_validated_coder
from coder.abstractCoder import AbstractCoder
# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR, remove
from os.path import exists


class DecodeTool(AbstractTool):
    """
    This class is a tool to decode the videos of the processing chain.
    """

    def __get_src_path(self, src_id, hrc_set, stream_mode):
        """
        Returns the path where the source is put to

        :param src_id: the id of the source to process
        :type src_id: int

        :param hrc_set: the hrc set to apply.
        :type hrc_set: dict

        :param stream_mode: the mode the source was streamed in.
        :type stream_mode: basestring

        :return: The path of where the source is put to
        :rtype: str
        """

        assert isinstance(src_id, int)
        assert isinstance(hrc_set, dict)
        assert isinstance(stream_mode, basestring)

        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set

        # get source path for MPEGTS video
        if stream_mode in (
            self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP,
            self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP
        ):
            return self._path + DECODER_SOURCE_DIR + PATH_SEPARATOR + self._get_output_file_name(
                src_id, hrc_set, EXTRACT_MPEGTS_EXTENSION
            )

        elif stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_RAW_RTP:

            codec = self._get_codec_by_hrc_set(hrc_set)

            return self._path + 'outputHevc' + PATH_SEPARATOR + self._get_output_file_name(
                src_id, hrc_set, codec.get_raw_file_extension()
            )

        else:
            raise KeyError('Invalid stream mode given in hrc_set with id %d!'
                           % hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID])

    def __decode_source_by_coder(self, src_id, hrc_set, coder):
        """
        Decodes a given source according to the given settings with the given coder.

        :param src_id: the id of the source to decode
        :type src_id; int

        :param hrc_set: the HRC settings to decode the source for
        :type hrc_set: dict

        :param coder: the coder to decode the source
        :type coder; AbstractCoder
        """
        assert isinstance(src_id, int)
        assert isinstance(hrc_set, dict)
        assert isinstance(coder, AbstractCoder)

        assert self._hrc_table.DB_TABLE_FIELD_NAME_STREAM_MODE in hrc_set
        stream_mode = hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_STREAM_MODE]

        #
        # Build source and destination path
        #

        src_path = self.__get_src_path(src_id, hrc_set, stream_mode)

        destination_path = self._path + DECODER_DESTINATION_DIR + PATH_SEPARATOR + self._get_output_file_name(
            src_id, hrc_set, DECODE_OUTPUT_FILE_TYPE_EXTENSION
        )

        # check if the destination path already exists -> check override mode to skip or to override
        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
        if exists(destination_path):
            if self._is_override_mode:
                if not self._is_dry_run:
                    remove(destination_path)
                print "# \033[95m\033[1mREMOVE src %d : hrc %d\033[0m"\
                      % (src_id, int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID]))
            else:
                print "# \033[95m\033[1mSKIP src %d : hrc %d\033[0m"\
                      % (src_id, int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID]))
                return

        #
        # Set coder log file
        #

        if self._log_folder:
            log_file_path = self._log_folder + PATH_SEPARATOR + self._get_output_file_name(src_id, hrc_set, 'log')
            coder.set_log_file(log_file_path)

        #
        # Decode payload file in src_path
        #

        coder.set_src_path(src_path) \
             .set_destination_path(destination_path)

        coder.decode_video()

    def __decode_source_with_hrc(self, source):
        """
        Goes through the connected HRC settings for a given source, re-streams and decodes it.

        :param source: the settings of the source to decode
        :type source: dict
        """

        assert isinstance(source, dict)
        assert self._src_table.DB_TABLE_FIELD_NAME_SRC_ID in source

        src_id = int(source[self._src_table.DB_TABLE_FIELD_NAME_SRC_ID])
        hrc_sets = self._pvs_matrix.get_hrc_sets_of_src_id(src_id)

        for hrc_set in hrc_sets:
            assert isinstance(hrc_set, dict)
            assert self._hrc_table.DB_TABLE_FIELD_NAME_CODER_ID in hrc_set

            coding_id = hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_CODER_ID]
            coder = get_validated_coder(coding_id, self._config.get_config_folder_path())
            coder.set_dry_mode(self._is_dry_run)

            self.__decode_source_by_coder(src_id, hrc_set, coder)

    def execute(self):
        """
        Executes the tool, i.e. it will decode all lossy pcap files, for which an HRC configuration is given in
        the PVS matrix
        """

        super(self.__class__, self).execute()

        for src_set in self._src_sets:
            try:
                self.__decode_source_with_hrc(src_set)
            except KeyError or Warning, e:
                self._append_exception(e)

        self._show_we_summary()