__author__ = 'Alexander Dethof'

from database.dbHandler import DbHandler
from metaConfig.metaConfigInterface import MetaConfigInterface

# List of database table field names
#
#


class EncodingTable(DbHandler, MetaConfigInterface):
    """
    Represents the table which includes all settings for the encoding procedure
    """

    DB_TABLE_NAME = 'encoding'

    # main encoding command link
    DB_TABLE_FIELD_NAME_ENCODING_ID = 'encoding_id'
    DB_TABLE_FIELD_NAME_CODEC_ID = 'codec_id'
    DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID = 'codec_settings_id'

    # general params
    DB_TABLE_FIELD_NAME_BIT_RATE = 'bit_rate'
    DB_TABLE_FIELD_NAME_FPS = 'fps'  # frames per second
    DB_TABLE_FIELD_NAME_RES = 'res'  # rescaling
    DB_TABLE_FIELD_NAME_TWO_PASS = 'two-pass'  # boolean settings if two pass encoding is allowed or not

    _valid_field_names = (
        # data set id
        DB_TABLE_FIELD_NAME_ENCODING_ID,

        # general encoding settings
        DB_TABLE_FIELD_NAME_BIT_RATE,
        DB_TABLE_FIELD_NAME_FPS,
        DB_TABLE_FIELD_NAME_RES,
        DB_TABLE_FIELD_NAME_TWO_PASS,

        # codec specific settings
        DB_TABLE_FIELD_NAME_CODEC_ID,
        DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            EncodingTable.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to specify different sets of encoding settings which can be used
 by different encoders, to encode an arbitrary video source.""",
            fields=[
                MetaTableField(
                    EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID,
                    int,
                    'unique id to identify the encoding data set'
                ),
                MetaTableField(
                    EncodingTable.DB_TABLE_FIELD_NAME_CODEC_ID,
                    str,
                    'unique name id to identify the codec used for the encoding operation'
                ),
                MetaTableField(
                    EncodingTable.DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID,
                    int,
                    'id to link these settings with the codec\'s appropriate settings'
                ),
                MetaTableField(
                    EncodingTable.DB_TABLE_FIELD_NAME_BIT_RATE,
                    int,
                    'bit rate the video should be encoded with (unit: kbit/s)'
                ),
                MetaTableField(
                    EncodingTable.DB_TABLE_FIELD_NAME_FPS,
                    int,
                    'number of frames to encode the video with (unit: frame/s)'
                ),
                MetaTableField(
                    EncodingTable.DB_TABLE_FIELD_NAME_TWO_PASS,
                    bool,
                    '0 if one-pass encoding should be used, 1 otherwise'
                )
            ]
        )

    def __init__(self, db_table_path, filters):
        """
        Initialization of the class by it's super class

        :param db_table_path: the path of the table (incl. name) to load
        :type db_table_path: basestring

        :param filters: filters which may apply to the table
        :type filters: dict
        """

        DbHandler.__init__(self, db_table_path, self.DB_TABLE_FIELD_NAME_ENCODING_ID, filters)

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :type row: dict

        :raises AssertionError: if an assertion failed during the validation
        """

        assert isinstance(row, dict)

        self._assert_fields(row, self.DB_TABLE_FIELD_NAME_ENCODING_ID, (
            self.DB_TABLE_FIELD_NAME_ENCODING_ID,
            self.DB_TABLE_FIELD_NAME_CODEC_ID,
            self.DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID,
            self.DB_TABLE_FIELD_NAME_BIT_RATE,
            self.DB_TABLE_FIELD_NAME_FPS,
            self.DB_TABLE_FIELD_NAME_RES,
            self.DB_TABLE_FIELD_NAME_TWO_PASS
        ))

        self._map_int(row, (
            self.DB_TABLE_FIELD_NAME_ENCODING_ID,
            self.DB_TABLE_FIELD_NAME_CODEC_SETTINGS_ID,
            self.DB_TABLE_FIELD_NAME_BIT_RATE,
            self.DB_TABLE_FIELD_NAME_FPS,
            (self.DB_TABLE_FIELD_NAME_TWO_PASS, 0, 1)
        ))