__author__ = 'Alexander Dethof'


from database.dbHandler import DbHandler
from metaConfig.metaConfigInterface import MetaConfigInterface


class PacketLossTable(DbHandler, MetaConfigInterface):
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

    DB_TABLE_FIELD_VALUE_MANIPULATOR_TOOL__NONE = 'none'
    DB_TABLE_FIELD_VALUE_MANIPULATOR_TOOL__TC = 'tc'
    DB_TABLE_FIELD_VALUE_MANIPULATOR_TOOL__TELCHEMY = 'telchemy'

    VALID_FIELD_VALUES__MANIPULATOR_TOOL = (
        DB_TABLE_FIELD_VALUE_MANIPULATOR_TOOL__NONE,
        DB_TABLE_FIELD_VALUE_MANIPULATOR_TOOL__TC,
        DB_TABLE_FIELD_VALUE_MANIPULATOR_TOOL__TELCHEMY
    )

    # valid field names used in the table
    _valid_field_names = (
        DB_TABLE_FIELD_NAME_PACKET_LOSS_ID,
        DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL,
        DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL_ID
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            PacketLossTable.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to set settings for packet loss manipulation, which can be
applied on different streamed sources.""",
            fields=[
                MetaTableField(
                    PacketLossTable.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID,
                    int,
                    'unique id identifying the packet loss settings'
                ),
                MetaTableField(
                    PacketLossTable.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL,
                    str,
                    'name of the manipulator tool to use',
                    PacketLossTable.VALID_FIELD_VALUES__MANIPULATOR_TOOL
                ),
                MetaTableField(
                    PacketLossTable.DB_TABLE_FIELD_NAME_MANIPULATOR_TOOL_ID,
                    int,
                    'unique id which refers to the manipulator\'s specific settings'
                )
            ]
        )

    # TODO add sub-tree!

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