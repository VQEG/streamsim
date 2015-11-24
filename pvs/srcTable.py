__author__ = 'Alexander Dethof'

from database.dbHandler import DbHandler


class SrcTable(DbHandler):
    """
    Represents the table which includes all settings for the source.
    """

    # general src fields
    DB_TABLE_FIELD_NAME_SRC_ID = 'src_id'
    DB_TABLE_FIELD_NAME_SRC_NAME = 'src_name'

    # valid field names used in the src table
    _valid_field_names = (
        DB_TABLE_FIELD_NAME_SRC_ID,
        DB_TABLE_FIELD_NAME_SRC_NAME
    )

    def __init__(self, db_table_path, filters):
        """
        Initialization of the class by it's super class

        :param db_table_path: the path of the table (incl. name) to load
        :type db_table_path: basestring
        """

        DbHandler.__init__(self, db_table_path, self.DB_TABLE_FIELD_NAME_SRC_ID, filters)

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :type row: dict

        :raises AssertionError: if an assertion failed during the validation
        """

        assert isinstance(row, dict)

        #
        # Check obligatory field
        #

        self._assert_fields(row, self.DB_TABLE_FIELD_NAME_SRC_ID, [
            self.DB_TABLE_FIELD_NAME_SRC_NAME
        ])