__author__ = 'Alexander Dethof'

from abc import ABCMeta, abstractmethod
from cmd.operator import Operator
from os.path import isfile


class AbstractCoder(Operator):
    """
    This class is used as abstract base for all coders written in the coder module. It forces a class extending
    this abstract one to have methods to deliver encoding, decoding, stream sending and stream receiving functionality.
    """

    # necessary to make this class abstract
    __metaclass__ = ABCMeta

    #
    # path configuration
    #

    # the path to the program of the coder which performs the encoding
    APP_PATH = ''  # TODO force properties to be set

    # the path to the program of the coder which performs the decoding
    APP_PATH = ''

    # the path to the program of the coder which performs the send operations for streaming
    STREAMER_PATH = ''  # TODO force properties to be set

    # defines the value of the src path field on class initialization
    DEFAULT_SRC_PATH = ''

    # defines the value of the destination path field on class initialization
    DEFAULT_DESTINATION_PATH = ''

    # defines the value of the log file path field on class initialization
    DEFAULT_LOG_FILE_PATH = ''

    #
    # list of available stream modes
    #

    # MPEG transport stream
    STREAM_MODE_MPEGTS = 'mpegts'

    # raw NAL units
    STREAM_MODE_RTP = 'rtp'

    # summary of all valid stream modes
    VALID_STREAM_MODES = (
        STREAM_MODE_MPEGTS,
        STREAM_MODE_RTP
    )

    def __init__(self, config_folder_path):
        """
        Initialization of the class, i.e. it will set the default values for the coder's src and desitnation path.
        Further more it will check if the configures pathes for the encoder, decoder and streamer (sending/receiving)
        software reference to an existing file.
        """

        Operator.__init__(self)

        self._src_path = self.DEFAULT_SRC_PATH
        self._destination_path = self.DEFAULT_DESTINATION_PATH
        self._log_file = self.DEFAULT_LOG_FILE_PATH
        self._config_folder_path = config_folder_path

        if not isfile(self.APP_PATH) and not self._is_dry_run:
            raise IOError(
                "The given ENCODER path `%s` is not a valid file path - please review the coder's configuration"
                % self.APP_PATH
            )

        if not isfile(self.STREAMER_PATH) and not self._is_dry_run:
            raise IOError(
                "The given STREAMER path `%s` is not a valid file path - please review the coder's configuration"
                % self.STREAMER_PATH
            )

    def set_src_path(self, src_path):
        """
        Configures the class's source path. This is the file on which the coder module will interact the next method
        calls, after this path has been set.

        :param src_path: the source which should be used for coder interaction
        :type src_path: basestring
        """

        assert isinstance(src_path, basestring), "The source path given to the code is not a string"
        assert isfile(src_path), "The source path `%s` given to the coder is not a valid file" % src_path

        self._src_path = src_path
        return self

    def set_destination_path(self, destination_path):
        """
        Sets the class's destination path, i.e. the file in which the results of the interaction can be written in.

        :param destination_path: the file in which the results of the coder's interaction can be written in
        :type destination_path: basestring
        """

        assert isinstance(destination_path, basestring)

        self._destination_path = destination_path
        return self

    def set_log_file(self, log_file):
        """
        Sets a log file which can be used for the coder's outputs

        :param log_file: The path to the file where the output should be logged in
        :type log_file: basestring

        :return: self
        :rtype: AbstractCoder
        """

        assert isinstance(log_file, basestring)

        self._log_file = log_file
        return self

    @abstractmethod
    def encode(self, encoding_set):
        """
        Abstract method which has to be implemented in all classes extending this one. Used to perform an interaction
        to encode a video.
        :param encoding_set: the data set containing all information for encoding processes
        """

        pass

    @abstractmethod
    def decode_video(self):
        """
        Abstract method which has to be implemented in all classes extending this one. Used to perform an interaction
        to decode a video.
        """

        pass

    @abstractmethod
    def send_stream(self, server, port, stream_mode, codec):
        """
        Abstract method which has to be implemented in all classes extending this one. Used to perform an interaction
        to send a video

        :param: server: the server to stream the data to
        :type server: basestring

        :param: port: the server's port to stream the data to
        :type port: int

        :param stream_mode: the mode which specifies how to stream the file
        :type stream_mode: basestring

        :param codec: the codec used for the encoding of the video (required to set bit stream filters)
        :type codec: AbstractCodec
        """

        pass