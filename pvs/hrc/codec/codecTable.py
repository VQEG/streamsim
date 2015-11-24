__author__ = 'Alexander Dethof'

from database.dbHandler import DbHandler


class CodecTable(DbHandler):
    """
    This class can represent any codec table in the codec configuration.
    """

    DB_TABLE_FIELD_NAME_ID = 'codec_settings_id'

    def __init__(self, db_table_path, valid_field_names):
        """
        Initialization of a new codec table.

        :param db_table_path: the path of the table
        :type db_table_path: basestring

        :param valid_field_names: the field names allowed to use in the table
        :type valid_field_names: list|tuple
        """

        self._valid_field_names = valid_field_names
        super(CodecTable, self).__init__(db_table_path, self.DB_TABLE_FIELD_NAME_ID)

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :type row: dict

        :raises AssertionError: if an assertion failed during the validation
        """

        assert isinstance(row, dict)

        self._assert_fields(row, self.DB_TABLE_FIELD_NAME_ID)
        self._map_int(row, self.DB_TABLE_FIELD_NAME_ID)

        # TODO validators for codec specific tables
