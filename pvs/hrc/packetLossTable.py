__author__ = 'Alexander Dethof'


from database.dbHandler import DbHandler


class PacketLossTable(DbHandler):
    """
    Class to represent the data table which delivers all information about the loss settings.
    """

    # name of the table
    DB_TABLE_NAME = 'packet_loss'

    # general table fields
    DB_TABLE_FIELD_NAME_PACKET_LOSS_ID = 'packet_loss_id'

    # specific loss setting fields
    DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL = 'manipulator_tool'
    DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL_ID = 'manipulator_tool_id'

    # valid field names used in the table
    _valid_field_names = (
        DB_TABLE_FIELD_NAME_PACKET_LOSS_ID,
        DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL,
        DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL_ID
    )

    def __init__(self, db_table_path, filters):
        """
        Initialization of the class by it's super class

        :param db_table_path: the path of the table (incl. name) to load
        :type db_table_path: basestring

        :param filters: filters which may apply to the table
        :type filters: dict
        """

        DbHandler.__init__(self, db_table_path, self.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID, filters)

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :type row: dict

        :raises AssertionError: if an assertion failed during the validation
        """

        self._assert_fields(row, self.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID, [
            self.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL
        ])

        if row[self.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL] != 'none':
            self._assert_fields(row, self.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID, [
                self.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL_ID
            ])

        self._map_int(row, [
            self.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID
        ])

        # TODO add validity for manipulator tool id