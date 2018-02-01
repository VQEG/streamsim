__author__ = 'Alexander Dethof'


from abstractCodec import AbstractCodec
from cmd.paramCollection import ParamCollection
from pvs.hrc.encodingTable import EncodingTable
from pvs.hrc.codec.codecTable import CodecTable


class X265Codec(AbstractCodec):
    """
    This class can be used to encode videos with the x265 codec.
    """

    DB_TABLE_NAME = 'x265'

    DB_TABLE_FIELD_NAME_PRESET = 'preset'
    DB_TABLE_FIELD_NAME_BFRAMES = 'bframes'
    DB_TABLE_FIELD_NAME_CRF = 'crf'
    DB_TABLE_FIELD_NAME_KEYINT = 'keyint'
    DB_TABLE_FIELD_NAME_MIN_KEYINT = 'min-keyint'
    DB_TABLE_FIELD_NAME_MERANGE = 'merange'
    DB_TABLE_FIELD_NAME_ME = 'me'
    DB_TABLE_FIELD_NAME_SLICES = 'slices'
    DB_TABLE_FIELD_NAME_BPYRAMID = 'bpyramid'

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
            X265Codec.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to define multiple individual x265 settings which can be applied
for video encoding techniques in the context of the processing chain.""",
            fields=[
                MetaTableField(
                    CodecTable.DB_TABLE_FIELD_NAME_ID,
                    int,
                    'unique integer value identifying the data set'
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_PRESET,
                    str,
                    'preset according to https://trac.ffmpeg.org/wiki/Encode/H.264#crf',
                    X265Codec.DB_TABLE_FIELD_PRESET_VALID_VALUES
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_CRF,
                    int,
                    'quantizer scale according to https://trac.ffmpeg.org/wiki/Encode/H.264#crf'
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_KEYINT,
                    int,
                    'similiar to gop length; defines the maximum number of frames between two I-frames'
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_MIN_KEYINT,
                    int,
                    'minimum distance between two I-frames'
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_MERANGE,
                    int,
                    'motion search range [default: 57]'
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_ME,
                    str,
                    'motion search method',
                    ('dia', 'hex [default]', 'umh', 'star', 'full')
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_SLICES,
                    int
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_BPYRAMID,
                    str,
                    'use, if possible, b-frames as references'
                ),
                MetaTableField(
                    X265Codec.DB_TABLE_FIELD_NAME_BFRAMES,
                    int,
                    'max number of consecutive b-frames'
                )
            ]
        )

    @staticmethod
    def get_bit_stream_parser(src_path):
        from bitstreamparse.rtp.hevc import Hevc as RtpHevc
        return RtpHevc(src_path)

    @staticmethod
    def get_library_name():
        """
        Returns the name of the codec's library where the codec is implemented in.

        :return: the name of the codec's library where the codec is implemented in
        :rtype: basestring
        """

        return 'libx265'

    @staticmethod
    def _get_codec_table_path():
        """
        Returns the table's path (inc. name) where the codec's settings are configured in

        :return: the table's path (inc. name) where the codec's settings are configured in
        :rtype: basestring
        """

        return 'codec/x265'

    @staticmethod
    def get_bit_stream_filter():
        """
        Returns, if available, a bit stream filter which should be used with this codec.
        :return: if available, a bit stream filter which should be used with this codec.
        :rtype: basestring
        """

        """
        Filter: hevc_mp4toannexb
        """ #TODO extend documentation about HEVC bit stream filter

        return 'hevc_mp4toannexb'

    @staticmethod
    def get_raw_file_extension():
        """
        Returns the file extension which can be used for raw encoded videos
        :return: file extension which can be used for raw encoded videos
        :rtype: basestring
        """

        return 'hevc'

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
            self.DB_TABLE_FIELD_NAME_BFRAMES,
            self.DB_TABLE_FIELD_NAME_CRF,
            self.DB_TABLE_FIELD_NAME_KEYINT,
            self.DB_TABLE_FIELD_NAME_MIN_KEYINT,
            self.DB_TABLE_FIELD_NAME_MERANGE,
            self.DB_TABLE_FIELD_NAME_ME,
            self.DB_TABLE_FIELD_NAME_SLICES,
            self.DB_TABLE_FIELD_NAME_BPYRAMID
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

        #add param for bframes settings, if configured
        if self.DB_TABLE_FIELD_NAME_BFRAMES in self._settings:
            """
            bframes <BFRAMES>:
                number of bframes in the video
                URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--bframes
            """
            params.set('bframes', int(self._encoding_settings[self.DB_TABLE_FIELD_NAME_BFRAMES]))

        if self.DB_TABLE_FIELD_NAME_KEYINT in self._settings:
            """
            keyint <KEYINT>:
                maximum number of I frames
                URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--keyint
            """
            params.set('keyint', int(self._settings[self.DB_TABLE_FIELD_NAME_KEYINT]))

        if self.DB_TABLE_FIELD_NAME_MIN_KEYINT in self._settings:
            """
            min-keyint <KEYINT_MIN>:
                minimum gop size
                URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--min-keyint
            """
            params.set('min-keyint', int(self._settings[self.DB_TABLE_FIELD_NAME_MIN_KEYINT]))

        if self.DB_TABLE_FIELD_NAME_MERANGE in self._settings:
            """
            merange <integer>:
                Motion search range. Default 57

                The default is derived from the default CTU size (64) minus the luma interpolation half-length (4)
                minus maximum subpel distance (2) minus one extra pixel just in case the hex search method is used.
                If the search range were any larger than this, another CTU row of latency would be required for
                reference frames.

                Range of values: an integer from 0 to 32768

                URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--merange
            """
            params.set('merange', int(self._settings[self.DB_TABLE_FIELD_NAME_MERANGE]))

        if self.DB_TABLE_FIELD_NAME_ME in self._settings:
            """
            me <integer|string>:
                Motion search method. Generally, the higher the number the harder the ME method will
                try to find an optimal match. Diamond search is the simplest. Hexagon search is a little better.
                Uneven Multi-Hexegon is an adaption of the search method used by x264 for slower presets. Star is
                a three step search adapted from the HM encoder: a star-pattern search followed by an optional
                radix scan followed by an optional star-search refinement. Full is an exhaustive search; an order
                of magnitude slower than all other searches but not much better than umh or star.
                   0. dia
                   1. hex (default)
                   2. umh
                   3. star
                   4. full
                   URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--me
            """
            params.set('me', self._settings[self.DB_TABLE_FIELD_NAME_ME])

        if self.DB_TABLE_FIELD_NAME_SLICES in self._settings:
            params.set('slices', int(self._settings[self.DB_TABLE_FIELD_NAME_SLICES]))

        if self.DB_TABLE_FIELD_NAME_BPYRAMID in self._settings:
            """
            b-pyramid:
                Use B-frames as references, when possible. Default enabled
                URL: http://x265.readthedocs.org/en/latest/cli.html#cmdoption--b-pyramid
            """
            params.set('b-pyramid', self._settings[self.DB_TABLE_FIELD_NAME_BPYRAMID])

        return params
