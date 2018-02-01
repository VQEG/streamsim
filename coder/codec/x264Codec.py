__author__ = 'Alexander Dethof'


from abstractCodec import AbstractCodec
from cmd.paramCollection import ParamCollection
from pvs.hrc.encodingTable import EncodingTable
from pvs.hrc.codec.codecTable import CodecTable


class X264Codec(AbstractCodec):
    """
    This class can be used to encode videos with the x264 codec.
    """

    DB_TABLE_NAME = 'x264'

    DB_TABLE_FIELD_NAME_PRESET = 'preset'
    DB_TABLE_FIELD_NAME_BFRAMES = 'bframes'
    DB_TABLE_FIELD_NAME_CRF = 'crf'
    DB_TABLE_FIELD_NAME_KEYINT = 'keyint'
    DB_TABLE_FIELD_NAME_MIN_KEYINT = 'min-keyint'

    DB_TABLE_FIELD_PRESET_VALUE_ULTRAFAST = 'ultrafast'
    DB_TABLE_FIELD_PRESET_VALUE_SUPERFAST = 'superfast'
    DB_TABLE_FIELD_PRESET_VALUE_VERYFAST = 'veryfast'
    DB_TABLE_FIELD_PRESET_VALUE_FASTER = 'faster'
    DB_TABLE_FIELD_PRESET_VALUE_FAST = 'fast'
    DB_TABLE_FIELD_PRESET_VALUE_MEDIUM = 'medium'
    DB_TABLE_FIELD_PRESET_VALUE_SLOW = 'slow'
    DB_TABLE_FIELD_PRESET_VALUE_SLOWER = 'slower'
    DB_TABLE_FIELD_PRESET_VALUE_VERYSLOW = 'veryslow'
    DB_TABLE_FIELD_PRESET_VALUE_PLACEBO = 'placebo'

    DB_TABLE_FIELD_PRESET_VALID_VALUES = (
        DB_TABLE_FIELD_PRESET_VALUE_ULTRAFAST,
        DB_TABLE_FIELD_PRESET_VALUE_SUPERFAST,
        DB_TABLE_FIELD_PRESET_VALUE_VERYFAST,
        DB_TABLE_FIELD_PRESET_VALUE_FASTER,
        DB_TABLE_FIELD_PRESET_VALUE_FAST,
        DB_TABLE_FIELD_PRESET_VALUE_MEDIUM,
        DB_TABLE_FIELD_PRESET_VALUE_SLOW,
        DB_TABLE_FIELD_PRESET_VALUE_SLOWER,
        DB_TABLE_FIELD_PRESET_VALUE_VERYSLOW,
        DB_TABLE_FIELD_PRESET_VALUE_PLACEBO
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            X264Codec.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to define multiple individual x264 settings which can be applied
for video encoding techniques in the context of the processing chain.""",
            fields=[
                MetaTableField(
                    CodecTable.DB_TABLE_FIELD_NAME_ID,
                    int,
                    'unique integer value identifying the data set'
                ),
                MetaTableField(
                    X264Codec.DB_TABLE_FIELD_NAME_PRESET,
                    str,
                    'preset according to https://trac.ffmpeg.org/wiki/Encode/H.264#crf',
                    X264Codec.DB_TABLE_FIELD_PRESET_VALID_VALUES
                ),
                MetaTableField(
                    X264Codec.DB_TABLE_FIELD_NAME_CRF,
                    int,
                    'quantizer scale according to https://trac.ffmpeg.org/wiki/Encode/H.264#crf'
                ),
                MetaTableField(
                    X264Codec.DB_TABLE_FIELD_NAME_KEYINT,
                    int,
                    'similiar to gop length; defines the maximum number of frames between two I-frames'
                ),
                MetaTableField(
                    X264Codec.DB_TABLE_FIELD_NAME_MIN_KEYINT,
                    int,
                    'minimum distance between two I-frames'
                )
            ]
        )

    @staticmethod
    def get_bit_stream_parser(src_path):
        raise Exception('Not implemented yet!')

    @staticmethod
    def get_library_name():
        """
        Returns the name of the codec's library where the codec is implemented in.

        :return: the name of the codec's library where the codec is implemented in
        :rtype: basestring
        """

        return 'libx264'

    @staticmethod
    def _get_codec_table_path():
        """
        Returns the table's path (inc. name) where the codec's settings are configured in

        :return: the table's path (inc. name) where the codec's settings are configured in
        :rtype: basestring
        """

        return 'codec/x264'

    @staticmethod
    def get_bit_stream_filter():
        """
        Returns, if available, a bit stream filter which should be used with this codec.
        :return: if available, a bit stream filter which should be used with this codec.
        :rtype: basestring
        """

        """
        Filter: h264_mp4toannexb

        `Convert an H.264 bitstream from length prefixed mode to start code prefixed mode
        (as defined in the Annex B of the ITU-T H.264 specification). This is required by some
        streaming formats, typically the MPEG-2 transport stream format ("mpegts").`

        Extracted from: https://www.ffmpeg.org/ffmpeg-bitstream-filters.html#h264_005fmp4toannexb
        """

        return 'h264_mp4toannexb'

    @staticmethod
    def get_raw_file_extension():
        """
        Returns the file extension which can be used for raw encoded videos
        :return: file extension which can be used for raw encoded videos
        :rtype: basestring
        """

        return 'h264'

    def _get_valid_field_names(self):
        """
        Returns a tuple of setting field name which can be processed in this codec.

        :return: a tuple of setting field name which can be processed in this codec
        :rtype: tuple
        """

        return (
            # main fields
            CodecTable.DB_TABLE_FIELD_NAME_ID,

            # configuration fields
            self.DB_TABLE_FIELD_NAME_PRESET,
            self.DB_TABLE_FIELD_NAME_BFRAMES,
            self.DB_TABLE_FIELD_NAME_CRF,
            self.DB_TABLE_FIELD_NAME_KEYINT,
            self.DB_TABLE_FIELD_NAME_MIN_KEYINT
        )

    def _validate_general_encoding_settings(self, encoding_settings):
        """
        Validates given encoding settings if they fit with the current codec settings.

        :param encoding_settings: the encoding settings to validate
        :type encoding_settings: dict

        :raise AssertionError: if a validation assertion fails
        """

        # check if a dictionary validation can be done on the given settings
        assert isinstance(encoding_settings, dict)

        # Exclusive CRF-Bit-Rate-Rule:
        # The settings are only allowed to use CRF or bit_rate as setting value - both should raise an error!
        assert (EncodingTable.DB_TABLE_FIELD_NAME_BIT_RATE in encoding_settings) \
            ^ (self.DB_TABLE_FIELD_NAME_CRF in self._settings), \
            self._build_err_msg(
                "In the codec settings a CRF value is defined although a bit rate was already defined in the "
                "general encoding settings!"
            )

    def get_settings_param_collection(self):
        """
        Returns a param collection which can be used a parameter in coding processes on the command line

        :return: param collection which can be used a parameter in coding processes on the command line
        :rtype: ParamCollection
        """

        # build params
        params = ParamCollection()

        """
        bframes <BFRAMES>:
            number of bframes in the video
            URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--bframes
        """
        if self.DB_TABLE_FIELD_NAME_BFRAMES in self._settings:
            params.set('bframes', int(self._encoding_settings[self.DB_TABLE_FIELD_NAME_BFRAMES]))

        """
        keyint <KEYINT>:
            maximum number of I frames
            URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--keyint
        """
        if self.DB_TABLE_FIELD_NAME_KEYINT in self._settings:
            params.set('keyint', int(self._settings[self.DB_TABLE_FIELD_NAME_KEYINT]))

        """
        min-keyint <KEYINT_MIN>:
            minimum gop size
            URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--min-keyint
        """
        if self.DB_TABLE_FIELD_NAME_MIN_KEYINT in self._settings:
            params.set('min-keyint', int(self._settings[self.DB_TABLE_FIELD_NAME_MIN_KEYINT]))

        return params
