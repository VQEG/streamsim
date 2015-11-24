__author__ = 'Alexander Dethof'

from abc import ABCMeta, abstractmethod
from pvs.hrc.codec.codecTable import CodecTable


class AbstractCodec(object):
    """
    Abstract class which should be used for codec classes to extend from. It delivers a method which automatically loads
    the settings from the appropriate codec configuration table and a method to migrate different settings.
    """

    # used to declare the class as abstract
    __metaclass__ = ABCMeta

    def __init__(self, codec_settings_id, config_folder_path):
        """
        Initialization of the codec class: It loads the settings of the given codec settings from the appropriate
         configuration table.

        :param codec_settings_id: the id of the codec settings specified in the appropriate table
        """

        assert isinstance(codec_settings_id, int)
        self._codec_settings_id = codec_settings_id

        codec_table_path = config_folder_path + self._get_codec_table_path()
        valid_field_names = self._get_valid_field_names()

        codec_table = CodecTable(codec_table_path, valid_field_names)

        self._settings = dict()
        self._codec_settings = codec_table.get_row_with_id(codec_settings_id)
        self._encoding_settings = {}

        self._migrate_settings()

    @staticmethod
    @abstractmethod
    def _get_codec_table_path():
        """
        Returns the path of the codec's configuration table.
        :return: the path of the codec's configuration table.
        :rtype: basestring
        """

        pass

    @staticmethod
    @abstractmethod
    def get_library_name():
        """
        Returns the name of the library in which the codec is implemented.
        :return: the name of the library in which the codec is implemented.
        :rtype: basestring
        """

        pass

    @staticmethod
    @abstractmethod
    def get_bit_stream_filter():
        """
        Returns, if available, a bit stream filter which should be used with this codec.
        :return: if available, a bit stream filter which should be used with this codec.
        :rtype: basestring
        """

        pass

    @staticmethod
    @abstractmethod
    def get_raw_file_extension():
        """
        Returns the file extension which can be used for raw encoded videos
        :return: file extension which can be used for raw encoded videos
        :rtype: basestring
        """

        pass

    @abstractmethod
    def _get_valid_field_names(self):
        """
        Returns a list of valid field names which can be evaluated in the codec settings table. All other field
        names will be ignored.
        :return: A list of valid field names which can be evaluated in the codec settings table.
        :rtype: list | tuple
        """

        pass

    @abstractmethod
    def get_settings_param_collection(self):
        """
        Returns a collection of params which can be used to configure the codec on an command line call.
        :return: a collection of params which can be used to configure the codec on an command line call.
        """

        pass

    @abstractmethod
    def _validate_general_encoding_settings(self, encoding_settings):
        """
        Validates given encoding settings if they match to the current codec settings or if they may raise conflicts.
        In this case errors are thrown.

        :param encoding_settings: the settings to validate
        """

        pass

    def _build_err_msg(self, msg):
        """
        This method can be used to create usable validation error messages. It returns a message according to the
        following scheme:

        "Validation problem in table `<TABLE_NAME>` (id=<SETTINGS_ID>): `<ERROR_MESSAGE>`"

        :param msg: the message to put out as the <ERROR_MESSAGE>
        :return: a usable validation error message according to the following scheme:
         "Validation problem in table `<TABLE_NAME>` (id=<SETTINGS_ID>): `<ERROR_MESSAGE>`"
        """

        return "Validation problem in table `%s` (id=%d): `%s`"\
               % (self._get_codec_table_path(), self._codec_settings_id, msg)

    def _migrate_settings(self):
        """
        Migrates the current codec settings with the general encoding settings. The codec settings can overwrite
        the encoding settings.
        """

        self._settings = self._encoding_settings
        self._settings.update(self._codec_settings)

    def set_general_encoding_settings(self, encoding_settings):
        """
        Sets the general encoding settings which should be used in addition to the general codec settings
        :param encoding_settings: the general encoding settings which should be used in addition to the general
         codec settings
        """

        self._validate_general_encoding_settings(encoding_settings)
        self._encoding_settings = encoding_settings
        self._migrate_settings()