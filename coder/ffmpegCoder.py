__author__ = 'Alexander Dethof'

from abstractCoder import AbstractCoder
from codec.abstractCodec import AbstractCodec
from cmd.command import Command
from cmd.commandCollection import CommandCollection
from pvs.srcTable import SrcTable
from pvs.hrcTable import HrcTable
from pvs.hrc.encodingTable import EncodingTable

# the main program path of the ffmpeg coder
APP_PATH = 'ffmpeg'


class FfmpegCoder(AbstractCoder):
    """
    Class which represents the FFMPEG coder. It can encode a raw video to HEVC, according to a given set of encoder
    settings, decode a packet stream to HEVC, send and receive a HEVC video stream.

    For more information about FFMPEG. search up this link: http://ffmpeg.org/ffmpeg.html#Main-options
    """

    # True if all ffmepg commands should allow debugging logs, false otherwise
    _GLOBAL_DEBUG_MODE = False

    def __init__(self, config_folder_path):
        """
        Initialization of the ffmpeg coder. Calls up the parent's class initialization and initializes the coder's xlib
        """
        AbstractCoder.__init__(self, config_folder_path)

    @staticmethod
    def __get_codec_specific_param_name(codec):
        """
        Returns the name used to identify the codec specific params in the encoder method
        :return: the name used to identify the codec specific params in the encoder method
        """

        assert isinstance(codec, AbstractCodec)

        from codec.x264Codec import X264Codec
        if isinstance(codec, X264Codec):
            return 'x264-params'

        from codec.x265Codec import X265Codec
        if isinstance(codec, X265Codec):
            return 'x265-params'

    def __get_codec(self, encoding_set):
        """
        Returns the codec connected to given encoding settings
        :param encoding_set: the encoding settings to get the codec for
        :return: the codec connected to the given encoding settings
        """

        assert isinstance(encoding_set, dict)

        assert EncodingTable.DB_TABLE_FIELD_NAME_CODEC_ID in encoding_set
        codec_id = encoding_set[EncodingTable.DB_TABLE_FIELD_NAME_CODEC_ID]

        assert EncodingTable.DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID in encoding_set
        codec_settings_id = int(encoding_set[EncodingTable.DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID])

        from coder.codec.codecList import get_codec
        return get_codec(codec_id, codec_settings_id, self._config_folder_path)

    @staticmethod
    def __get_io_file_format(stream_mode):
        """
        Returns the value for ffmpeg's "f" parameter, which is used to set the streaming format

        :param stream_mode: the format configured in the stream settings
        :type stream_mode: basestring

        :return: the value for ffmpeg's "f" parameter, which is used to set the streaming format
        :rtype: basestring
        """

        assert isinstance(stream_mode, basestring)
        assert stream_mode in HrcTable.VALID_STREAM_MODES

        if stream_mode == HrcTable.DB_STREAM_MODE_FIELD_VALUE_RAW_RTP:
            return 'rtp'

        if stream_mode == HrcTable.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP:
            return 'mpegts'

        if stream_mode == HrcTable.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP:
            return 'rtp_mpegts'

    @staticmethod
    def __get_stream_protocol(stream_mode):
        """
        Returns the protocol which should be used for the appropriate streaming modes.

        :param stream_mode: The stream mode which is specified in the streaming settings.
        :type stream_mode: basestring

        :return: The protocol which should be used for the appropriate streaming modes
        :rtype: basestring
        """

        assert isinstance(stream_mode, basestring)
        assert stream_mode in HrcTable.VALID_STREAM_MODES

        if stream_mode == HrcTable.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP:
            return 'rtp'

        udp_formats = (
            HrcTable.DB_STREAM_MODE_FIELD_VALUE_RAW_RTP,
            HrcTable.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP
        )

        if stream_mode in udp_formats:
            return 'udp'

    def __get_general_encoding_command_without_destination(self, encoding_set, is_debug_mode):
        """
        Returns the general encoding command without a destination path. After adding a destination path it
        can be directly executed or further modified (useful for twopass coding)

        :param encoding_set: the configuration set describing the encoding configuration
        :type encoding_set: dict

        :param is_debug_mode: True is debug logging is allowed, False otherwise
        :type is_debug_mode: bool

        :return: the general encoding command without a destination path.
        :rtype: Command
        """

        assert self._src_path != self.DEFAULT_SRC_PATH
        assert self._destination_path != self.DEFAULT_DESTINATION_PATH
        assert isinstance(encoding_set, dict)

        codec = self.__get_codec(encoding_set)
        codec.set_general_encoding_settings(encoding_set)

        # build encoder command
        command = Command(APP_PATH)

        """
        -y: overwrite output file in each case without asking
        """
        command.set_as_posix_option('y')

        """
        -i <INPUT_FILE>: defines the input file
        """
        command.set_as_posix_option('i', self._src_path)

        """
        -c:v <CODEC>: sets the video codec
        """
        command.set_as_posix_option('c:v', codec.get_library_name())

        """
        -s <FRAME_SIZE>: defines the frames' size
        """
        assert SrcTable.DB_TABLE_FIELD_NAME_RES in encoding_set
        command.set_as_posix_option('s', encoding_set[SrcTable.DB_TABLE_FIELD_NAME_RES])

        """
        -r <FPS>: sets the frame rate (frames/second)
        """
        assert SrcTable.DB_TABLE_FIELD_NAME_FPS in encoding_set
        fps = encoding_set[SrcTable.DB_TABLE_FIELD_NAME_FPS]
        if fps:
            command.set_as_posix_option('r', float(fps))

        """
        -b:v <BIT_RATE>: defines the bit rate
        """
        assert EncodingTable.DB_TABLE_FIELD_NAME_BIT_RATE in encoding_set
        command.set_as_posix_option('b:v', '%dk' % int(encoding_set[EncodingTable.DB_TABLE_FIELD_NAME_BIT_RATE]))

        """
        append codec specific params
        """
        codec_params_name = self.__get_codec_specific_param_name(codec)
        codec_params = codec.get_settings_param_collection()
        if codec_params:
            command.set_as_posix_option(codec_params_name, str(codec_params))

        """
        set command's log output file
        """
        command.set_as_log_file(self._log_file) \
               .set_std_err_redirect_to_file()

        """
        SET DEBUG LOG
        """
        if is_debug_mode:
            command.set_as_posix_option('loglevel', 'debug')

        return command

    def __one_pass_encoding(self, encoding_set, is_debug_mode):
        """
        Executes a single encoding command according to the coder's source/destination-path configuration.

        :param encoding_set: the configuration set describing the encoder's settings
        :type encoding_set: dict

        :param is_debug_mode: True is debug logging is allowed, False otherwise
        :type is_debug_mode: bool
        """

        encoding_command = self.__get_general_encoding_command_without_destination(encoding_set, is_debug_mode)

        """
        add output file information
        """
        encoding_command.set_as_argument('DESTINATION', self._destination_path)

        # execute command
        self._cmd(encoding_command)

    def __two_pass_encoding(self, encoding_set, is_debug_mode):
        """
        Executes a two encoding commands according to the coder's source/destination-path configuration for two-pass
        coding. The first encoding command will write the output to devnull.

        :param encoding_set: the configuration set describing the encoder's settings
        :type encoding_set: dict

        :param is_debug_mode: True is debug logging is allowed, False otherwise
        :type is_debug_mode: bool
        """

        first_pass_command = self.__get_general_encoding_command_without_destination(encoding_set, is_debug_mode)

        from copy import deepcopy
        two_pass_command = deepcopy(first_pass_command)

        from os import devnull
        first_pass_command.set_as_posix_option('pass', 1)
        first_pass_command.set_as_posix_option('f', 'mp4')
        first_pass_command.set_as_argument('DESTINATION', devnull)

        two_pass_command.set_as_posix_option('pass', 2)
        two_pass_command.set_as_argument('DESTINATION', self._destination_path)

        encoding_command_collection = CommandCollection(first_pass_command, two_pass_command)

        self._cmd(encoding_command_collection)

    def encode(self, encoding_set, is_debug_mode=_GLOBAL_DEBUG_MODE):
        """
        Encodes the coder's source (raw video) to the coder's destination (hevc) according to the configuration given
        as argument.

        :param encoding_set: the data set containing all encoding information
        :type encoding_set: basestring

        :param is_debug_mode: True is debug logging is allowed, False otherwise
        :type is_debug_mode: bool
        """

        assert isinstance(encoding_set, dict)
        assert EncodingTable.DB_TABLE_FIELD_NAME_TWO_PASS in encoding_set

        if bool(int(encoding_set[EncodingTable.DB_TABLE_FIELD_NAME_TWO_PASS])):
            self.__two_pass_encoding(encoding_set, is_debug_mode)
        else:
            self.__one_pass_encoding(encoding_set, is_debug_mode)

    def decode_video(self, is_debug_mode=_GLOBAL_DEBUG_MODE):
        """
        Receives a video stream from the given stream configuration and returns a process which is able to decode
        this stream

        :param is_debug_mode: True, will allow debug logging of the command, False will disallow this.
        :type is_debug_mode: bool

        :param is_debug_mode: True is debug logging is allowed, False otherwise
        :type is_debug_mode: bool
        """

        command = Command(APP_PATH)

        """
        -y: override without asking
        """
        command.set_as_posix_option('y')

        """
        -i <INPUT>: defines the input stream
        """
        command.set_as_posix_option('i', self._src_path)

        """
        -c:v <CODEC_TYPE>: sets the video codec
        """
        command.set_as_posix_option('c:v', 'rawvideo')

        """
        <OUTPUT>: file where the decoded video should be stored in
        """
        command.set_as_argument('DESTINATION', self._destination_path)

        """
        set commands log output
        """
        command.set_as_log_file(self._log_file) \
               .set_std_err_redirect_to_file()

        """
        SET DEBUG LOG
        """
        if is_debug_mode:
            command.set_as_posix_option('loglevel', 'debug')

        # execute command
        return self._cmd(command)

    def send_stream(self, server, port, stream_mode, codec, is_debug_mode=_GLOBAL_DEBUG_MODE):
        """
        Streams the ffmpeg video to a given server:port by a given protocol.

        :param server: the server to stream to
        :type port: int

        :param port: the port to stream to
        :type server: basestring

        :param stream_mode: the mode how to stream the video
        :type stream_mode: basestring

        :param codec: the codec used for the encoding of the video (required to set bit stream filters)
        :type codec: AbstractCodec

        :param is_debug_mode: True is debug logging is allowed, False otherwise
        :type is_debug_mode: bool
        """

        assert isinstance(server, basestring)
        assert isinstance(port, int)
        assert isinstance(stream_mode, basestring)

        assert stream_mode in HrcTable.VALID_STREAM_MODES

        # build streaming command
        command = Command(APP_PATH)

        """
        -re: play back in real-time
        """
        command.set_as_posix_option('re')
        command.set_as_posix_option('y')

        """
        -i <INPUT_FILE>: defines the input file
        """
        command.set_as_posix_option('i', self._src_path)

        """
        -c:v sets the video codec
        """
        if stream_mode == HrcTable.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP:
            command.set_as_posix_option('c:v', 'copy')
        else:
            command.set_as_posix_option('c:v', codec.get_library_name()) # FIXME just for debug!!


        """
        -an (<OUTPUT>): disable audio output
        """
        command.set_as_posix_option('an')

        """
        -f <FMT> (<INPUT/OUTPUT>): force the input/output file format to <FMT>. In general the output format is
        automatically detected by the given input files, so this option is usually not needed.
        """
        command.set_as_posix_option('f', self.__get_io_file_format(stream_mode))

        """
        -bsf:v <FILTER>: sets a filter operation on the stream
        """
        if stream_mode in (
            HrcTable.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP,
            HrcTable.DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP
        ):
            bsf_name = codec.get_bit_stream_filter()
            if bsf_name:
                command.set_as_posix_option('bsf:v', bsf_name)

        if stream_mode == HrcTable.DB_STREAM_MODE_FIELD_VALUE_RAW_RTP:
            """
            -sdp_file <SDP_FILE_PATH>: path where to dump the sdp file content
            """

            # noinspection PyPep8Naming
            from os.path import splitext, extsep as FILE_EXTENSION_SEPARATOR
            (base_path, extension) = splitext(self._src_path)
            command.set_as_posix_option('sdp_file', base_path + FILE_EXTENSION_SEPARATOR + 'sdp')


        """
        address where to send the stream to
        """
        command.set_as_argument('DESTINATION', '%s://%s:%d' % (self.__get_stream_protocol(stream_mode), server, port))

        # TODO only for debug
        # command.set_as_argument('DEST2', 'test.ts');
        # TODO /only for debug

        """
        set the commands log output
        """
        command.set_as_log_file(self._log_file) \
               .set_std_err_redirect_to_file()

        """
        SET DEBUG LOG
        """
        if is_debug_mode:
            command.set_as_posix_option('loglevel', 'debug')

        # execute command
        self._cmd(command)