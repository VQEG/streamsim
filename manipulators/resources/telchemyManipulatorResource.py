__author__ = 'Alexander Dethof'


from database.dbHandler import DbHandler
from metaConfig.metaConfigInterface import MetaConfigInterface


class TelchemyManipulatorResource(DbHandler, MetaConfigInterface):

    DB_TABLE_NAME = 'telchemy'

    DB_FIELD_NAME_ID = 'id'
    DB_FIELD_MANIPULATION_TYPE = 'man_type'
    DB_FIELD_MANIPULATION_ID = 'man_id'

    MANIPULATION_TYPE_MARKOV = 'm'
    MANIPULATION_TYPE_READ_TRACE = 'r'

    VALID_MANIPULATION_TYPES = (
        MANIPULATION_TYPE_MARKOV,
        MANIPULATION_TYPE_READ_TRACE
    )

    _valid_field_names = (
        DB_FIELD_NAME_ID,
        DB_FIELD_MANIPULATION_TYPE,
        DB_FIELD_MANIPULATION_ID
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        config = MetaTable(
            TelchemyManipulatorResource.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to configure different individual setting combination which can
be used to manipulate .pcap files with the telchemy tpkloss tool.""",
            fields=[
                MetaTableField(
                    TelchemyManipulatorResource.DB_FIELD_NAME_ID,
                    int,
                    'unique id to identify each data set individually'
                ),
                MetaTableField(
                    TelchemyManipulatorResource.DB_FIELD_MANIPULATION_TYPE,
                    str,
                    'defines the manipulation model to use for the manipulation',
                    {
                        TelchemyManipulatorResource.MANIPULATION_TYPE_MARKOV:
                            'use a markov model (further specifications in %s table)'
                            % TelchemyManipulatorMarkovResource.DB_TABLE_NAME,
                        TelchemyManipulatorResource.MANIPULATION_TYPE_READ_TRACE:
                            'read a trace (further specifications in %s table)'
                            % TelchemyManipulatorReadTraceResource.DB_TABLE_NAME
                    }
                ),
                MetaTableField(
                    TelchemyManipulatorResource.DB_FIELD_MANIPULATION_ID,
                    int,
                    'id to identify the settings linked to the appropriate manipulation'
                )
            ]
        )

        config.add_children([
            TelchemyManipulatorReadTraceResource.get_meta_description(),
            TelchemyManipulatorMarkovResource.get_meta_description()
        ])

        return config

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :type row: dict

        :raises AssertionError: if an assertion failed during the validation
        """

        #
        # Check obligatory field
        #

        self._assert_fields(row, self.DB_FIELD_NAME_ID, (
            self.DB_FIELD_MANIPULATION_TYPE,
            self.DB_FIELD_MANIPULATION_ID
        ))

        #
        # Check and set values
        #

        self._map_int(row, (
            self.DB_FIELD_NAME_ID,
            self.DB_FIELD_MANIPULATION_ID
        ))

        assert row[self.DB_FIELD_MANIPULATION_TYPE] in self.VALID_MANIPULATION_TYPES, \
            "Unknown value for field `%s` given: `%s`, expected on of these: [%s]" \
            % (
                self.DB_FIELD_MANIPULATION_TYPE,
                row[self.DB_FIELD_MANIPULATION_TYPE],
                self.VALID_MANIPULATION_TYPES
            )


class TelchemyManipulatorReadTraceResource(DbHandler, MetaConfigInterface):

    DB_TABLE_NAME = 'read_trace'

    DB_FIELD_NAME_ID = 'id'
    DB_FIELD_NAME_TRACE_FILE_NAME = 'trace_file_name'

    _valid_field_names = (
        DB_FIELD_NAME_ID,
        DB_FIELD_NAME_TRACE_FILE_NAME
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            TelchemyManipulatorReadTraceResource.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to configure different individual setting combination which can
be used to manipulate .pcap files with the telchemy tpkloss tool, but only for trace reading applications.""",
            fields=[
                MetaTableField(
                    TelchemyManipulatorReadTraceResource.DB_FIELD_NAME_ID,
                    int,
                    'unique id to identify each data set individually'
                ),
                MetaTableField(
                    TelchemyManipulatorReadTraceResource.DB_FIELD_NAME_TRACE_FILE_NAME,
                    str,
                    """a relative file path to a loss trace, which is looked up in the folder PATH/traces (with PATH as
the path defined at the chain's execution time with the "p"/"path" argument)"""
                )
            ]
        )

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :raises AssertionError: if an assertion failed during the validation
        """

        #
        # Check obligatory field
        #

        self._assert_fields(row, self.DB_FIELD_NAME_ID, [
            self.DB_FIELD_NAME_TRACE_FILE_NAME
        ])

        self._map_int(row, self.DB_FIELD_NAME_ID)


class TelchemyManipulatorMarkovResource(DbHandler, MetaConfigInterface):

    DB_TABLE_NAME = 'markov'

    DB_FIELD_NAME_ID = 'id'
    DB_FIELD_MARKOV_TYPE = 'markov_type'
    DB_FIELD_MARKOV_ID = 'markov_id'
    DB_FIELD_START_AFTER = 'start_after'
    DB_FIELD_END_BEFORE = 'end_before'

    DB_FIELD_VALUE_MARKOV_TYPE_2STATE_VALUE = '2s'
    DB_FIELD_VALUE_MARKOV_TYPE_4STATE_VALUE = '4s'
    DB_FIELD_VALUE_MARKOV_TYPE_PNAMSPBNAMS_4STATE_VALUE = 'p4'

    VALID_MARKOV_TYPES = (
        DB_FIELD_VALUE_MARKOV_TYPE_2STATE_VALUE,
        DB_FIELD_VALUE_MARKOV_TYPE_4STATE_VALUE,
        DB_FIELD_VALUE_MARKOV_TYPE_PNAMSPBNAMS_4STATE_VALUE
    )

    _valid_field_names = (
        DB_FIELD_NAME_ID,
        DB_FIELD_MARKOV_TYPE,
        DB_FIELD_MARKOV_ID,
        DB_FIELD_START_AFTER,
        DB_FIELD_END_BEFORE
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        config = MetaTable(
            TelchemyManipulatorMarkovResource.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to configure different individual setting combination which can
be used to manipulate .pcap files with the telchemy tpkloss tool, but only for markov models.""",
            fields=[
                MetaTableField(
                    TelchemyManipulatorMarkovResource.DB_FIELD_NAME_ID,
                    int,
                    'unique id to identify each data set individually'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkovResource.DB_FIELD_MARKOV_TYPE,
                    str,
                    'markov model to use for the manipulation',
                    {
                        TelchemyManipulatorMarkovResource.DB_FIELD_VALUE_MARKOV_TYPE_2STATE_VALUE:
                            '2-state markov model (config in: %s/%s table)' % (
                                TelchemyManipulatorResource.DB_TABLE_NAME,
                                TelchemyManipulatorMarkov2StateResource.DB_TABLE_NAME
                            ),
                        TelchemyManipulatorMarkovResource.DB_FIELD_VALUE_MARKOV_TYPE_4STATE_VALUE:
                            '4-state markov model (config in: %s/%s table)' % (
                                TelchemyManipulatorResource.DB_TABLE_NAME,
                                TelchemyManipulatorMarkov4StateResource.DB_TABLE_NAME
                            ),
                        TelchemyManipulatorMarkovResource.DB_FIELD_VALUE_MARKOV_TYPE_PNAMSPBNAMS_4STATE_VALUE:
                            'P.NAMS/P.NBAMS 4-state markov model (config in: %s/%s table)' % (
                                TelchemyManipulatorResource.DB_TABLE_NAME,
                                TelchemyManipulatorMarkovPNamsPNBams4StateResource.DB_TABLE_NAME
                            )
                    }
                ),
                MetaTableField(
                    TelchemyManipulatorMarkovResource.DB_FIELD_MARKOV_ID,
                    int,
                    'id to identify the settings linked to the appropriate models'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkovResource.DB_FIELD_START_AFTER,
                    int,
                    'time in ms after the transmission\'s beginning, when the manipulation should start'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkovResource.DB_FIELD_END_BEFORE,
                    int,
                    'time in ms before the transmission\'s end, when the manipulation should stop'
                ),
            ]
        )

        config.add_children([
            TelchemyManipulatorMarkov2StateResource.get_meta_description(),
            TelchemyManipulatorMarkov4StateResource.get_meta_description(),
            TelchemyManipulatorMarkovPNamsPNBams4StateResource.get_meta_description()
        ])

        return config

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :raise AssertionError: if an assertion failed during the validation
        """

        #
        # Check obligatory field
        #

        self._assert_fields(row, self.DB_FIELD_NAME_ID, (
            self.DB_FIELD_MARKOV_TYPE,
            self.DB_FIELD_MARKOV_ID,
            self.DB_FIELD_START_AFTER,
            self.DB_FIELD_END_BEFORE
        ))

        #
        # check and set values
        #

        self._map_int(row, (
            self.DB_FIELD_NAME_ID,
            self.DB_FIELD_MARKOV_ID,
            self.DB_FIELD_START_AFTER,
            self.DB_FIELD_END_BEFORE
        ))

        # check validity of markov id
        assert row[self.DB_FIELD_MARKOV_TYPE] in self.VALID_MARKOV_TYPES, \
            "Unknown value for field `%s` given: `%s`, expected on of these: [%s]" \
            % (
                self.DB_FIELD_MARKOV_TYPE,
                row[self.DB_FIELD_MARKOV_TYPE],
                self.VALID_MARKOV_TYPES
            )


class TelchemyManipulatorMarkov2StateResource(DbHandler, MetaConfigInterface):

    DB_TABLE_NAME = 'markov2state'

    DB_FIELD_NAME_ID = 'id'
    DB_FIELD_NAME_PCB = 'pcb'
    DB_FIELD_NAME_PBC = 'pbc'
    DB_FIELD_NAME_G = 'g'
    DB_FIELD_NAME_B = 'b'

    _valid_field_names = (
        DB_FIELD_NAME_ID,
        DB_FIELD_NAME_PCB,
        DB_FIELD_NAME_PBC,
        DB_FIELD_NAME_G,
        DB_FIELD_NAME_B
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            TelchemyManipulatorMarkov2StateResource.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to configure different data sets for individual 2-state markov
models which can be used for packet manipulation purposes by telchemy.""",
            fields=[
                MetaTableField(
                    TelchemyManipulatorMarkov2StateResource.DB_FIELD_NAME_ID,
                    int,
                    'unique id to identify the model in the table'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov2StateResource.DB_FIELD_NAME_PCB,
                    float,
                    'Transition probability from burst to gap state'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov2StateResource.DB_FIELD_NAME_PBC,
                    float,
                    'Transition probability from gap to burst state'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov2StateResource.DB_FIELD_NAME_G,
                    float,
                    'Loss probability in gap state'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov2StateResource.DB_FIELD_NAME_B,
                    float,
                    'Loss probability in burst state'
                )
            ],
            footer_doc='Source: http://vqegstl.ugent.be/?q=node/27'
        )

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :raise AssertionError: if an assertion failed during the validation
        """

        #
        # Check obligatory field
        #

        self._assert_fields(row, self.DB_FIELD_NAME_ID, (
            self.DB_FIELD_NAME_PCB,
            self.DB_FIELD_NAME_PBC,
            self.DB_FIELD_NAME_G,
            self.DB_FIELD_NAME_B
        ))

        #
        # check and set values
        #

        self._map_int(row, self.DB_FIELD_NAME_ID)
        self._map_float(row, (
            self.DB_FIELD_NAME_PCB,
            self.DB_FIELD_NAME_PBC,
            self.DB_FIELD_NAME_G,
            self.DB_FIELD_NAME_B
        ), 0, 100)


class TelchemyManipulatorMarkov4StateResource(DbHandler, MetaConfigInterface):

    DB_TABLE_NAME = 'markov4state'

    DB_FIELD_NAME_ID = 'id'
    DB_FIELD_NAME_PBA = 'pba'
    DB_FIELD_NAME_PBC = 'pbc'
    DB_FIELD_NAME_PDC = 'pdc'
    DB_FIELD_NAME_PCD = 'pcd'
    DB_FIELD_NAME_PCB = 'pcb'
    DB_FIELD_NAME_G = 'g'
    DB_FIELD_NAME_B = 'b'

    _valid_field_names = (
        DB_FIELD_NAME_ID,
        DB_FIELD_NAME_PBA,
        DB_FIELD_NAME_PBC,
        DB_FIELD_NAME_PDC,
        DB_FIELD_NAME_PCD,
        DB_FIELD_NAME_PCB,
        DB_FIELD_NAME_G,
        DB_FIELD_NAME_B
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            TelchemyManipulatorMarkov4StateResource.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to configure different 4-state markov models which can be used
then by the telchemy tool to manipulate different pcap files with loss behaviour.""",
            fields=[
                MetaTableField(
                    TelchemyManipulatorMarkov4StateResource.DB_FIELD_NAME_ID,
                    int,
                    'unique id to identify each data set individually'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov4StateResource.DB_FIELD_NAME_PBA,
                    float,
                    'Transition probability from gap lossless to gap lossy state'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov4StateResource.DB_FIELD_NAME_PBC,
                    float,
                    'Transition probability from gap to gap burst state'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov4StateResource.DB_FIELD_NAME_PDC,
                    float,
                    'Transition probability from burst lossless to burst lossy state [default: 0.25]'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov4StateResource.DB_FIELD_NAME_PCD,
                    float,
                    'Transition probability from burst lossy to burst lossless state [default: 0.05]'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov4StateResource.DB_FIELD_NAME_PCB,
                    float,
                    'Transition probability from burst to gap state [default: 0.3]'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov4StateResource.DB_FIELD_NAME_G,
                    float,
                    'Loss probability in gap state'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkov4StateResource.DB_FIELD_NAME_B,
                    float,
                    'Loss probability in burst state'
                )
            ],
            footer_doc='Source: http://vqegstl.ugent.be/?q=node/27'
        )

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :raise AssertionError: if an assertion failed during the validation
        """

        assert isinstance(row, dict)

        #
        # Check obligatory field
        #

        self._assert_fields(row, self.DB_FIELD_NAME_ID, (
            self.DB_FIELD_NAME_PBA,
            self.DB_FIELD_NAME_PBC,
            self.DB_FIELD_NAME_G,
            self.DB_FIELD_NAME_B
        ))

        #
        # check and set values
        #

        self._map_int(row, self.DB_FIELD_NAME_ID)
        self._map_float(row, (
            self.DB_FIELD_NAME_PBA,
            self.DB_FIELD_NAME_PBC,
            self.DB_FIELD_NAME_G,
            self.DB_FIELD_NAME_B
        ), 0, 100)

        if self.DB_FIELD_NAME_PDC in row:
            self._map_float(row, self.DB_FIELD_NAME_PDC, 0, 100)

        if self.DB_FIELD_NAME_PCD in row:
            self._map_float(row, self.DB_FIELD_NAME_PCD, 0, 100)

        if self.DB_FIELD_NAME_PCB in row:
            self._map_float(row, self.DB_FIELD_NAME_PCB, 0, 100)


class TelchemyManipulatorMarkovPNamsPNBams4StateResource(DbHandler, MetaConfigInterface):

    DB_TABLE_NAME = 'pnamspnbams4'

    DB_FIELD_NAME_ID = 'id'
    DB_FIELD_NAME_LOSS_RATIO = 'loss_ratio'
    DB_FIELD_NAME_GAP_RATIO = 'gap_ratio'

    _valid_field_names = (
        DB_FIELD_NAME_ID,
        DB_FIELD_NAME_LOSS_RATIO,
        DB_FIELD_NAME_GAP_RATIO
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            TelchemyManipulatorMarkovPNamsPNBams4StateResource.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to specify different P.NAMS/P.NBAMS 4-state markov models for
the telchemy tool in order to manipulate packets with it.""",
            fields=[
                MetaTableField(
                    TelchemyManipulatorMarkovPNamsPNBams4StateResource.DB_FIELD_NAME_ID,
                    int,
                    'unique id to identify the model in the table'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkovPNamsPNBams4StateResource.DB_FIELD_NAME_LOSS_RATIO,
                    float,
                    'Target average loss probability in %'
                ),
                MetaTableField(
                    TelchemyManipulatorMarkovPNamsPNBams4StateResource.DB_FIELD_NAME_GAP_RATIO,
                    float,
                    'Percentage of time in which the process resides in the gap state (in %)'
                )
            ]
        )

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :raise AssertionError: if an assertion failed during the validation
        """

        #
        # Check obligatory field
        #

        self._assert_fields(row, self.DB_FIELD_NAME_ID, (
            self.DB_FIELD_NAME_LOSS_RATIO,
            self.DB_FIELD_NAME_GAP_RATIO
        ))

        #
        # check and set values
        #

        self._map_int(row, self.DB_FIELD_NAME_ID)
        self._map_float(row, (
            self.DB_FIELD_NAME_LOSS_RATIO,
            self.DB_FIELD_NAME_GAP_RATIO
        ), 0, 100)