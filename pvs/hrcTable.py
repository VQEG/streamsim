__author__ = 'Alexander Dethof'

from database.dbHandler import DbHandler
from metaConfig.metaConfigInterface import MetaConfigInterface
from hrc.encodingTable import EncodingTable
from hrc.packetLossTable import PacketLossTable
# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR


class HrcTable(DbHandler, MetaConfigInterface):
    """
    Represents the table containing all information about the HRC part of the PVS matrix, i.e. it delivers
    a link for each source to the appropriate encoding and loss insertion settings.
    """

    # hrc own fields
    DB_TABLE_FIELD_NAME_CODER_ID = 'coder_id'
    DB_TABLE_FIELD_NAME_HRC_ID = 'hrc_id'
    DB_TABLE_FIELD_NAME_STREAM_MODE = 'stream_mode'

    # stream mode values
    DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP = 'mpegts-rtp'
    DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP = 'mpegts-udp'
    DB_STREAM_MODE_FIELD_VALUE_RAW_RTP = 'raw-rtp'

    # valid stream modes
    VALID_STREAM_MODES = (
        DB_STREAM_MODE_FIELD_VALUE_MPEGTS_RTP,
        DB_STREAM_MODE_FIELD_VALUE_MPEGTS_UDP,
        DB_STREAM_MODE_FIELD_VALUE_RAW_RTP
    )

    # valid field names in the hrc table
    _valid_field_names = (
        DB_TABLE_FIELD_NAME_HRC_ID,
        EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID,
        PacketLossTable.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID,
        DB_TABLE_FIELD_NAME_CODER_ID,
        DB_TABLE_FIELD_NAME_STREAM_MODE
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        config = MetaTable(
            'hrc',
            header_doc="""In this csv file you are able to link different settings together which can be applied on an
arbitrary source.""",
            fields=[
                MetaTableField(
                    HrcTable.DB_TABLE_FIELD_NAME_HRC_ID,
                    int,
                    'unique id for each individual HRC data set used to reference it'
                ),
                MetaTableField(
                    EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID,
                    int,
                    'id of the settings used for encoding (Defined in the hrc/encoding.csv file)'
                ),
                MetaTableField(
                    PacketLossTable.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID,
                    int,
                    'id of the settings used for packet manipulation (Defined in the hrc/packet_loss.csv file)'
                ),
                MetaTableField(
                    HrcTable.DB_TABLE_FIELD_NAME_CODER_ID,
                    str,
                    'name of the coder to use for encoding, streaming and decoding'
                ),
                MetaTableField(
                    HrcTable.DB_TABLE_FIELD_NAME_STREAM_MODE,
                    str,
                    'mode in which the file should be streamed',
                    HrcTable.VALID_STREAM_MODES
                )
            ]
        )

        # build sub-tree from hrc
        config.add_children([EncodingTable.get_meta_description(), PacketLossTable.get_meta_description()])
        return config

    def __init__(self, db_table_path, filters):
        """
        Initialization of the class by it's super class and linking the appropriate hrc sub tables for encoding
        and packet loss settings.

        :param db_table_path: the path of the table (incl. name) to load
        :type db_table_path: basestring

        :param filters: filters which may apply on the table
        :type filters: dict
        """

        assert isinstance(db_table_path, basestring)
        assert isinstance(filters, dict)

        packet_loss_filters = dict()
        encoding_filters = dict()

        if 'encoding' in filters:
            encoding_filters = filters.pop('encoding')

        if 'packet_loss' in filters:
            packet_loss_filters = filters.pop('packet_loss')

        DbHandler.__init__(self, db_table_path, self.DB_TABLE_FIELD_NAME_HRC_ID, filters)

        self.__encoding_table = EncodingTable(
            db_table_path + PATH_SEPARATOR + EncodingTable.DB_TABLE_NAME,
            encoding_filters
        )

        self.__packet_loss_table = PacketLossTable(
            db_table_path + PATH_SEPARATOR + PacketLossTable.DB_TABLE_NAME,
            packet_loss_filters
        )

        self.__cleanup_filters()

    def __cleanup_filters(self):
        """
        Goes through the HRC sub tables and looks up, if entries have been herein filtered. If so, the linked data sets
        of the HRC table will be removed too.
        """

        rows = self.get_rows()
        remove_ids = list()
        for row in rows:
            packet_loss_id = int(row[PacketLossTable.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID])
            encoding_id = int(row[EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID])
            data_set_id = int(row[self.DB_TABLE_FIELD_NAME_HRC_ID])
            if self.__packet_loss_table.is_filtered(packet_loss_id) or self.__encoding_table.is_filtered(encoding_id):
                remove_ids.append(data_set_id)

        for remove_id in remove_ids:
            self._remove(remove_id)

    def get_encoding_table(self):
        """
        Returns the instance of the table containing all settings for the encoding procedure

        :return: the instance of the table containing all settings for the encoding procedure
        :rtype: EncodingTable
        """

        return self.__encoding_table

    def get_packet_loss_table(self):
        """
        Returns the instance of the table containing all settings for the loss insertion procedure

        :return: the instance of the table containing all settings for the loss insertion procedure
        :rtype: PacketLossTable
        """

        return self.__packet_loss_table

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

        self._assert_fields(row, self.DB_TABLE_FIELD_NAME_HRC_ID, (
            EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID,
            PacketLossTable.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID,
            self.DB_TABLE_FIELD_NAME_CODER_ID,
            self.DB_TABLE_FIELD_NAME_STREAM_MODE
        ))

        #
        # check and set values
        #

        self._map_int(row, (
            self.DB_TABLE_FIELD_NAME_HRC_ID,
            EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID,
            PacketLossTable.DB_TABLE_FIELD_NAME_PACKET_LOSS_ID
        ))

        # check validity of markov id
        assert row[self.DB_TABLE_FIELD_NAME_STREAM_MODE] in self.VALID_STREAM_MODES, \
            "Unknown value for field `%s` given: `%s`, expected on of these: [%s]" \
            % (
                self.DB_TABLE_FIELD_NAME_STREAM_MODE,
                row[self.DB_TABLE_FIELD_NAME_STREAM_MODE],
                self.VALID_STREAM_MODES
            )

        # check coder id
        from coder.coderList import VALID_CODER_IDS
        assert row[self.DB_TABLE_FIELD_NAME_CODER_ID] in VALID_CODER_IDS, \
            "Unknown value for field `%s` given: `%s`, expected on of these: [%s]" \
            % (
                self.DB_TABLE_FIELD_NAME_CODER_ID,
                row[self.DB_TABLE_FIELD_NAME_CODER_ID],
                VALID_CODER_IDS
            )