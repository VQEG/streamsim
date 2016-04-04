__author__ = 'Alexander Dethof'

from database.dbHandler import DbHandler
from metaConfig.metaConfigInterface import MetaConfigInterface


class SrcTable(DbHandler, MetaConfigInterface):
    """
    Represents the table which includes all settings for the source.
    """

    # general src fields
    DB_TABLE_FIELD_NAME_SRC_ID = 'src_id'
    DB_TABLE_FIELD_NAME_SRC_NAME = 'src_name'
    DB_TABLE_FIELD_NAME_FPS = 'fps'
    DB_TABLE_FIELD_NAME_RES = 'res'

    # valid field names used in the src table
    _valid_field_names = (
        DB_TABLE_FIELD_NAME_SRC_ID,
        DB_TABLE_FIELD_NAME_SRC_NAME,
        DB_TABLE_FIELD_NAME_RES,
        DB_TABLE_FIELD_NAME_FPS
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            'src',
            header_doc="""In this csv file you are able to specify which link resources should be used to perform
operations on in the processing chain. Be aware that each file listed here must exists in the "srcVid" folder.""",
            fields=[
                MetaTableField(
                    SrcTable.DB_TABLE_FIELD_NAME_SRC_ID,
                    int,
                    'unique id to identify each individual source'
                ),
                MetaTableField(
                    SrcTable.DB_TABLE_FIELD_NAME_SRC_NAME,
                    str,
                    'unique name to identify the source file in the folder "srcVid"'
                ),
                MetaTableField(
                    SrcTable.DB_TABLE_FIELD_NAME_RES,
                    str,
                    'video frame resolution in px'
                ),
                MetaTableField(
                    SrcTable.DB_TABLE_FIELD_NAME_FPS,
                    int,
                    'number of frames to encode the video with (unit: frame/s)'
                ),
            ]
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
            self.DB_TABLE_FIELD_NAME_SRC_NAME,
            self.DB_TABLE_FIELD_NAME_FPS,
            self.DB_TABLE_FIELD_NAME_RES
        ])

        self._map_int(row, (
            self.DB_TABLE_FIELD_NAME_FPS
        ))