__author__ = 'Alexander Dethof'

STREAM_PORT = 1234
STREAM_SERVER = '127.0.0.1'
STREAM_PROTOCOL_UDP = 'udp'
STREAM_PROTOCOL_RTP = 'rtp'
STREAM_NETWORK_INTERFACE = 'lo'

from encodeTool import ENCODER_DESTINATION_DIR
STREAM_SOURCE_DIR = ENCODER_DESTINATION_DIR
STREAM_DESTINATION_DIR = 'outputPcap'
STREAM_OUTPUT_FILE_TYPE_EXTENSION = 'pcap'

TOOL_ID_STREAM = 'stream_videos'

from abstractTool import AbstractTool
# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR, remove
from os.path import isfile, exists
from cmd.command import Command
from coder.coderList import get_validated_coder
from multiprocessing.process import Process


class StreamTool(AbstractTool):
    """
    This class is a tool which collects on execution all videos in the source dir and streams them with their
     appropriate coders. To each stream tcpdump will listen and dump each packet into a separate PCAP-file.
    """

    def __convert_via_mp4box_to_new_format(self, input_path, file_output_format_extension):
        """

        :param input_path:
        :param file_output_format_extension:
        :return:
        """

        assert isinstance(input_path, basestring)
        assert isinstance(file_output_format_extension, basestring)
        assert isfile(input_path)
        assert exists(input_path)

        """
        MP4BOX: http://gpac.wp.mines-telecom.fr/mp4box/
        """
        mp4box_command = Command('MP4Box')

        """
        -add <INPUT>: specifies the file to convert
        """

        mp4box_command.set_as_posix_option('add', input_path)

        """
        <INPUT> the path to convert in
        """
        output_file_path = self._switch_file_extension(input_path, file_output_format_extension)
        mp4box_command.set_as_argument('OUTPUT', output_file_path)

        """
        set log output
        """
        if self._log_folder:
            from os.path import splitext, basename, extsep
            mp42ts_log_file_path = self._log_folder \
                                 + PATH_SEPARATOR \
                                 + 'mp42ts_' \
                                 + splitext(basename(input_path))[0] \
                                 + extsep \
                                 + 'log'

            mp4box_command.set_as_log_file(mp42ts_log_file_path) \
                          .set_std_err_redirect_to_file()

        self._cmd(mp4box_command)

        return output_file_path

    def __convert_to_mpeg2ts(self, input_path, codec_name):
        """
        Converts an input file to a specific output format with MP4Box to MPEG2-TS

        :param input_path: the path to the file to convert
        :type input_path: basestring

        :param codec_name: the name of the codec to use for the conversion
        :type codec_name: basestring

        :return: the path where the converted file can be found after the operation succeeded
        :rtype: basestring
        """

        assert isinstance(input_path, basestring)
        assert isinstance(codec_name, basestring)
        assert isfile(input_path)
        assert exists(input_path)

        """
        ffmpeg: http://ffmpeg.org/
        """
        from coder.ffmpegCoder import APP_PATH as FFMPEG_PATH
        ffmpeg_command = Command(FFMPEG_PATH)

        """
        i: input file
        """
        ffmpeg_command.set_as_posix_option('i', input_path)

        """
        c: codec used
        """
        ffmpeg_command.set_as_posix_option('c:v', codec_name)

        """
        set output file
        """
        output_path = self._switch_file_extension(input_path, 'ts')
        ffmpeg_command.set_as_argument('OUTPUT', output_path)

        """
        set log output
        """
        if self._log_folder:
            from os.path import splitext, basename, extsep
            mp42ts_log_file_path = self._log_folder \
                                 + PATH_SEPARATOR \
                                 + 'mp42ts_' \
                                 + splitext(basename(input_path))[0] \
                                 + extsep \
                                 + 'log'

            ffmpeg_command.set_as_log_file(mp42ts_log_file_path) \
                          .set_std_err_redirect_to_file()

        ffmpeg_process = self._cmd(ffmpeg_command)

        if isinstance(ffmpeg_process, Process):
            ffmpeg_process.join()

        return output_path

    def __stream_source_by_hrc_set(self, src_id, hrc_set):
        """
        Streams a source by the given settings of the HRC table
        :param src_id: the id of the source to send the stream
        :param hrc_set: the set which contains all information
        """

        assert isinstance(src_id, int)
        assert isinstance(hrc_set, dict)

        codec = self._get_codec_by_hrc_set(hrc_set)
        file_path = self._path + STREAM_SOURCE_DIR + PATH_SEPARATOR + self._get_output_file_name(
            src_id, hrc_set, 'mov'  # codec.get_raw_file_extension() # TODOwebtv999
        )

        if not isfile(file_path):
            raise Warning(
                'Source %d could not be streamed, because no appropriate file has been found' % src_id
            )

        pcap_path = self._path + STREAM_DESTINATION_DIR + PATH_SEPARATOR + self._get_output_file_name(
            src_id, hrc_set, STREAM_OUTPUT_FILE_TYPE_EXTENSION
        )

        # check if the destination path already exists -> check override mode to skip or to override
        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
        if exists(pcap_path):
            if self._is_override_mode:
                if not self._is_dry_run:
                    remove(pcap_path)
                print "# \033[95m\033[1mREMOVE src %d : hrc %d\033[0m"\
                      % (src_id, int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID]))
            else:
                assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
                print "# \033[95m\033[1mSKIP src %d : hrc %d\033[0m"\
                      % (src_id, int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID]))
                return

        # setup coder
        coder_id = hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_CODER_ID]
        coder = get_validated_coder(coder_id, self._config.get_config_folder_path())

        assert self._hrc_table.DB_TABLE_FIELD_NAME_STREAM_MODE in hrc_set
        stream_mode = hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_STREAM_MODE]

        if stream_mode == self._hrc_table.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP:
            file_path = self.__convert_to_mpeg2ts(file_path, codec.get_library_name())

        coder.set_src_path(file_path)

        if self._log_folder:
            coder_log_file_path = self._log_folder \
                                  + PATH_SEPARATOR \
                                  + coder.__class__.__name__ \
                                  + '_' \
                                  + self._get_output_file_name(src_id, hrc_set, 'log')
            coder.set_log_file(coder_log_file_path)

        #
        # Activate tcp dump to record the streamed packets
        #

        """
        tcpdump: http://www.tcpdump.org/tcpdump_man.html

        -i <INPUT>: specifies input resource
        -w <OUTPUT>: specifies output resource to write pcap content

        additional filter used here: '<PROTOCOL> port <PORT>'
        --> Capture only all packets which are delivered via the <PROTOCOL> protocol over port <PORT>
        """
        tcpdump_command = Command('tcpdump')
        tcpdump_command.set_as_subprocess() \
            .set_as_posix_option('i', STREAM_NETWORK_INTERFACE) \
            .set_as_posix_option('w', pcap_path) \
            .set_as_argument('PROTOCOL', STREAM_PROTOCOL_UDP) \
            .set_as_argument('PORT', 'port %d' % STREAM_PORT)

        # set tcpdump log
        if self._log_folder:
            tcpdump_log_file_path = self._log_folder \
                                    + PATH_SEPARATOR \
                                    + 'tcpdump_' \
                                    + self._get_output_file_name(src_id, hrc_set, 'log')
            tcpdump_command.set_as_log_file(tcpdump_log_file_path) \
                .set_std_err_redirect_to_file()

        tcpdump_process = self._cmd(tcpdump_command)

        if not self._is_dry_run:
            from time import sleep
            sleep(1)

        #
        # Stream video
        #

        coder.set_dry_mode(self._is_dry_run) \
             .send_stream(
                STREAM_SERVER,
                STREAM_PORT,
                stream_mode,
                codec
             )

        #
        # Stop tcpdump
        #

        if isinstance(tcpdump_process, Process):
            self._terminate_process_with_children(tcpdump_process)

    def __stream_source(self, source):
        """
        Identifies the coding id of a given video source and streams it by this coder.
        :param source: the source to stream
        """

        assert isinstance(source, dict)

        assert self._src_table.DB_TABLE_FIELD_NAME_SRC_ID in source
        src_id = int(source[self._src_table.DB_TABLE_FIELD_NAME_SRC_ID])
        hrc_sets = self._pvs_matrix.get_hrc_sets_of_src_id(src_id)

        for hrc_set in hrc_sets:
            try:
                self.__stream_source_by_hrc_set(src_id, hrc_set)
            except (KeyError, AssertionError, Warning) as e:
                # Several errors can be logged separately and do not need to be thrown immediately (would only disturb
                # the whole process) - these errors will be caught and summarized later
                self._append_exception(e)

    def execute(self):
        """
        Main function which can be called to run the tool execution. It will can the stream source dir and
        try to stream each video in their over its appropriate coder.
        """

        super(self.__class__, self).execute()

        for src_set in self._src_sets:
            self.__stream_source(src_set)

        # show summary of all logged exceptions
        self._show_we_summary()