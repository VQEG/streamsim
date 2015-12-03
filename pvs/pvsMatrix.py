__author__ = 'Alexander Dethof'

from database import dbTable
from srcTable import SrcTable
from hrcTable import HrcTable
from filters.filterSet import FilterSet
from metaConfig.metaConfigInterface import MetaConfigInterface


class PvsMatrix(MetaConfigInterface):
    """
    This class represents the pvs matrix, which contains all information about the sources and settings to be used in
    the processing chain.
    """

    # available filter group ids
    FILTER_GROUP_ID_SRC_TABLE = 'src'
    FILTER_GROUP_ID_HRC_TABLE = 'hrc'

    # general pvs matrix fields
    DB_TABLE_FIELD_NAME_PVS_ID = 'pvs_id'

    # valid field names which are allowed in the pvs matrix data table
    __valid_field_names = (
        DB_TABLE_FIELD_NAME_PVS_ID,
        SrcTable.DB_TABLE_FIELD_NAME_SRC_ID,
        HrcTable.DB_TABLE_FIELD_NAME_HRC_ID
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            'pvs',
            header_doc="""In this csv-file you are able to link sources with different HRC settings multiply.
Remember to set for each individual connection a unique id.""",
            fields=[
                MetaTableField(
                    PvsMatrix.DB_TABLE_FIELD_NAME_PVS_ID,
                    int,
                    'unique id for each connection'
                ),
                MetaTableField(
                    SrcTable.DB_TABLE_FIELD_NAME_SRC_ID,
                    int,
                    'id of the source (specified in the source table) to link with the HRC'
                ),
                MetaTableField(
                    HrcTable.DB_TABLE_FIELD_NAME_HRC_ID,
                    int,
                    'id of the HRC setting to link with the source'
                )
            ]
        )

    def __init__(self, pvs_path, src_path, hrc_path, filters):
        """
        Main initialisation of the PVS matrix. It will initialize the PVS, SRC and HRC table instances and connect
        the HRC sets with the SRC ids in an internal data structure to ease common access.

        :param pvs_path: the path where to load the PVS table from
        :type pvs_path: basestring

        :param src_path: the path where to load the SRC table from
        :type src_path: basestring

        :param hrc_path: the path where to load the HRC table from
        :type hrc_path: basestring

        :param filters: filters to be set on the configuration
        :type filters: FilterSet
        """

        # Validate input arguments
        assert isinstance(pvs_path, basestring)
        assert isinstance(src_path, basestring)
        assert isinstance(hrc_path, basestring)
        assert isinstance(filters, FilterSet)

        # load pvs table
        self.__pvs_table = dbTable.DbTable(
            pvs_path,
            self.DB_TABLE_FIELD_NAME_PVS_ID,
            self.__valid_field_names
        )

        # load src and hrc references
        self.__src_table = SrcTable(src_path, filters.get_filter_group(self.FILTER_GROUP_ID_SRC_TABLE))
        self.__hrc_table = HrcTable(hrc_path, filters.get_filter_group(self.FILTER_GROUP_ID_HRC_TABLE))

        # build src2hrc mappings
        self.__build_src2hrc_mappings()

    def __build_src2hrc_mappings(self):
        """
        Goes through all hrc sets of the hrc table and maps them with the appropriate source ids in a dictionary.
        """

        self.__src2hrc_mappings = dict()
        pvs_sets = self.__pvs_table.get_rows()
        for pvs_set in pvs_sets:
            assert isinstance(pvs_set, dict)
            assert self.__src_table.DB_TABLE_FIELD_NAME_SRC_ID in pvs_set
            src_id = int(pvs_set[self.__src_table.DB_TABLE_FIELD_NAME_SRC_ID])
            if src_id not in self.__src2hrc_mappings:
                self.__src2hrc_mappings[src_id] = list()

            assert self.__hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in pvs_set
            hrc_id = int(pvs_set[self.__hrc_table.DB_TABLE_FIELD_NAME_HRC_ID])
            if self.__hrc_table.has_row_with_id(hrc_id):
                self.__src2hrc_mappings[src_id].append(hrc_id)

    def get_src_table(self):
        """
        Returns the instance of the src table

        :return: instance of the src table
        :rtype: SrcTable
        """

        return self.__src_table

    def get_hrc_table(self):
        """
        Returns the instance of the hrc table

        :return: instance of the hrc table
        :rtype: HrcTable
        """

        return self.__hrc_table

    def get_hrc_sets_of_src_id(self, src_id):
        """
        Returns all hrc sets which are linked to the given source id

        :param src_id: the source to return the appropriate hrc sets for
        :type src_id: int

        :return: all hrc sets which are linked to the given source id
        :rtype: dict[]
        """

        assert isinstance(src_id, int)

        try:
            hrc_ids = self.__src2hrc_mappings[src_id]
        except:
            raise KeyError('Could not load HRC definition for src_id=%d' % src_id)

        return [self.__hrc_table.get_row_with_id(hrc_id) for hrc_id in hrc_ids]