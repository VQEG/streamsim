__author__ = 'Alexander Dethof'

from database.dbHandler import DbHandler
from metaConfig.metaConfigInterface import MetaConfigInterface


class TrafficControlManipulatorResource(DbHandler, MetaConfigInterface):
    """

    """

    DB_TABLE_NAME = 'tc'

    DB_ID_FIELD_NAME = 'id'
    DB_DELAY_FIELD_NAME = 'delay'
    DB_JITTER_FIELD_NAME = 'jitter'
    DB_JITTER_DISTRIBUTION_FIELD_NAME = 'distribution'
    DB_LOSS_MODE_FIELD_NAME = 'loss_mode'
    DB_LOSS_MODE_ID_FIELD_NAME = 'loss_mode_id'

    # configure delay values
    DB_DELAY_VALUE_NONE = 0

    # configure jitter distribution values
    DB_JITTER_DISTRIBUTION_VALUE_NONE = 'none'
    DB_JITTER_DISTRIBUTION_VALUE_UNIFORM = 'uniform'
    DB_JITTER_DISTRIBUTION_VALUE_NORMAL = 'normal'
    DB_JITTER_DISTRIBUTION_VALUE_PARETO = 'pareto'
    DB_JITTER_DISTRIBUTION_VALUE_PARETONORMAL = 'paretonormal'

    DB_JITTER_DISTRIBUTION_VALID_VALUES = (
        DB_JITTER_DISTRIBUTION_VALUE_NONE,
        DB_JITTER_DISTRIBUTION_VALUE_UNIFORM,
        DB_JITTER_DISTRIBUTION_VALUE_NORMAL,
        DB_JITTER_DISTRIBUTION_VALUE_PARETO,
        DB_JITTER_DISTRIBUTION_VALUE_PARETONORMAL
    )

    # configure loss modes
    DB_LOSS_MODE_RANDOM_VALUE = 'random'
    DB_LOSS_MODE_STATE_VALUE = 'state'
    DB_LOSS_MODE_GE_VALUE = 'gemodel'

    DB_LOSS_MODE_VALID_VALUES = (
        DB_LOSS_MODE_RANDOM_VALUE,
        DB_LOSS_MODE_STATE_VALUE,
        DB_LOSS_MODE_GE_VALUE
    )

    _valid_field_names = (
        DB_ID_FIELD_NAME,
        DB_DELAY_FIELD_NAME,
        DB_JITTER_FIELD_NAME,
        DB_JITTER_DISTRIBUTION_FIELD_NAME,
        DB_LOSS_MODE_FIELD_NAME,
        DB_LOSS_MODE_ID_FIELD_NAME
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        config = MetaTable(
            TrafficControlManipulatorResource.DB_TABLE_NAME,
            header_doc="""In this file you are able to configure the traffic control manipulator tool for
online manipulation.""",
            fields=[
                MetaTableField(
                    TrafficControlManipulatorResource.DB_ID_FIELD_NAME,
                    int,
                    'unique id to identify the control data set'
                ),
                MetaTableField(
                    TrafficControlManipulatorResource.DB_DELAY_FIELD_NAME,
                    float,
                    'delay in ms which may occur on the packet transmission'
                ),
                MetaTableField(
                    TrafficControlManipulatorResource.DB_JITTER_FIELD_NAME,
                    float,
                    'jitter in ms in which the delay may vary'
                ),
                MetaTableField(
                    TrafficControlManipulatorResource.DB_JITTER_DISTRIBUTION_FIELD_NAME,
                    str,
                    'specification of the jitter distribution',
                    TrafficControlManipulatorResource.DB_JITTER_DISTRIBUTION_VALID_VALUES
                ),
                MetaTableField(
                    TrafficControlManipulatorResource.DB_LOSS_MODE_FIELD_NAME,
                    str,
                    """specifies in which mode the packets transmission should be manipulated,
i.e. which model should be applied on""",
                    {
                        TrafficControlManipulatorResource.DB_LOSS_MODE_RANDOM_VALUE:
                            'loss is randomly distributed',
                        TrafficControlManipulatorResource.DB_LOSS_MODE_STATE_VALUE:
                            'loss is distributed via markov model settings',
                        TrafficControlManipulatorResource.DB_LOSS_MODE_GE_VALUE:
                            'loss is distributed via Gilbert-Elliot models'
                    }
                ),
                MetaTableField(
                    TrafficControlManipulatorResource.DB_LOSS_MODE_ID_FIELD_NAME,
                    int,
                    """an arbitrary, but unique, id referencing to a configuration set of the appropriate loss_mode,
the referenced configuration can be set in the tc configuration folders (look up the file according to the mode's
name!)"""
                )
            ]
        )

        config.add_children([
            TrafficControlManipulatorGeModelResource.get_meta_description(),
            TrafficControlManipulatorStateModeResource.get_meta_description(),
            TrafficControlManipulatorRandomModeResource.get_meta_description()
        ])

        return config

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :raise AssertionError: if an assertion failed during the validation
        """

        #
        # Check mandatory fields
        #

        assert self.DB_ID_FIELD_NAME in row
        assert self.DB_DELAY_FIELD_NAME in row
        assert self.DB_JITTER_DISTRIBUTION_FIELD_NAME in row
        assert self.DB_LOSS_MODE_ID_FIELD_NAME in row

        #
        # check and set values
        #

        self._map_int(row, self.DB_ID_FIELD_NAME)
        self._map_float(row, self.DB_DELAY_FIELD_NAME)

        if row[self.DB_JITTER_DISTRIBUTION_FIELD_NAME] != self.DB_JITTER_DISTRIBUTION_VALUE_NONE:
            assert self.DB_JITTER_FIELD_NAME in row
            self._map_float(row, self.DB_JITTER_FIELD_NAME)

        self._map_val_range(row, self.DB_JITTER_DISTRIBUTION_FIELD_NAME, self.DB_JITTER_DISTRIBUTION_VALID_VALUES)

        self._map_val_range(row, self.DB_LOSS_MODE_FIELD_NAME, self.DB_LOSS_MODE_VALID_VALUES)

        self._map_int(row, self.DB_LOSS_MODE_ID_FIELD_NAME)


class TrafficControlManipulatorRandomModeResource(DbHandler, MetaConfigInterface):
    """

    """

    DB_TABLE_NAME = 'random'

    DB_ID_FIELD_NAME = 'id'
    DB_LOSS_RATE_FIELD_NAME = 'loss_rate'

    _valid_field_names = (
        DB_ID_FIELD_NAME,
        DB_LOSS_RATE_FIELD_NAME
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            TrafficControlManipulatorRandomModeResource.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to configure individual data sets which can be used as random
loss models for the tc packet manipulation tool.""",
            fields=[
                MetaTableField(
                    TrafficControlManipulatorRandomModeResource.DB_ID_FIELD_NAME,
                    int,
                    'unique number to identify each data set individually'
                ),
                MetaTableField(
                    TrafficControlManipulatorRandomModeResource.DB_LOSS_RATE_FIELD_NAME,
                    float,
                    'loss rate in percent (%) which may apply in this model'
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
        # check obligatory fields
        #

        assert self.DB_ID_FIELD_NAME in row, \
            "The given row [%s] does not contain an id field!" % row

        assert self.DB_LOSS_RATE_FIELD_NAME in row, \
            "The given row with id %d does not contain a `%s` probability factor!" % (
                row[self.DB_ID_FIELD_NAME], self.DB_LOSS_RATE_FIELD_NAME
            )

        #
        # check and set values
        #

        self._map_int(row, self.DB_ID_FIELD_NAME)
        self._map_float(row, self.DB_LOSS_RATE_FIELD_NAME, 0, 100)


class TrafficControlManipulatorStateModeResource(DbHandler, MetaConfigInterface):
    """

    """

    DB_TABLE_NAME = 'state'

    DB_ID_FIELD_NAME = 'id'
    DB_P13_FIELD_NAME = 'p13'
    DB_P31_FIELD_NAME = 'p31'
    DB_P32_FIELD_NAME = 'p32'
    DB_P23_FIELD_NAME = 'p23'
    DB_P14_FIELD_NAME = 'p14'

    _valid_field_names = (
        DB_ID_FIELD_NAME,
        DB_P13_FIELD_NAME,
        DB_P31_FIELD_NAME,
        DB_P32_FIELD_NAME,
        DB_P23_FIELD_NAME,
        DB_P14_FIELD_NAME,
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            TrafficControlManipulatorStateModeResource.DB_TABLE_NAME,
            header_doc="""In this csv file you are able to configure individual markov models which can be used by the
tc online network manipulator to insert packet loss into an ongoing transmission.""",
            fields=[
                MetaTableField(
                    TrafficControlManipulatorStateModeResource.DB_ID_FIELD_NAME,
                    int,
                    'unique id to identify each data set individually'
                ),
                MetaTableField(
                    TrafficControlManipulatorStateModeResource.DB_P13_FIELD_NAME,
                    float,
                    'probability in percent (%) for the good reception'
                ),
                MetaTableField(
                    TrafficControlManipulatorStateModeResource.DB_P31_FIELD_NAME,
                    float,
                    '[optional] probability in percent (%)'
                ),
                MetaTableField(
                    TrafficControlManipulatorStateModeResource.DB_P32_FIELD_NAME,
                    float,
                    '[optional] probability in percent (%)'
                ),
                MetaTableField(
                    TrafficControlManipulatorStateModeResource.DB_P23_FIELD_NAME,
                    float,
                    '[optional] probability in percent (%)'
                ),
                MetaTableField(
                    TrafficControlManipulatorStateModeResource.DB_P14_FIELD_NAME,
                    float,
                    '[optional] probability in percent (%)'
                )
            ],
            footer_doc="""* if %s is set only => Bernoulli Model
* With %s the configuration above is extended to a 2-State Markov Model (Good reception within a burst)
* With %s and %s the configuration above is extended to a 3-State Markov Model (Burst losses)
* With %s the configuration above is extended to a 4-State Markov Model (Independent losses)""" % (
                TrafficControlManipulatorStateModeResource.DB_P13_FIELD_NAME,

                TrafficControlManipulatorStateModeResource.DB_P31_FIELD_NAME,

                TrafficControlManipulatorStateModeResource.DB_P32_FIELD_NAME,
                TrafficControlManipulatorStateModeResource.DB_P23_FIELD_NAME,

                TrafficControlManipulatorStateModeResource.DB_P14_FIELD_NAME
            )
        )

    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not

        :param row: the row to validate
        :raise AssertionError: if an assertion failed during the validation
        """

        #
        # check obligatory fields
        #

        assert self.DB_ID_FIELD_NAME in row, \
            "The given row [%s] does not contain an id field!" % row

        assert self.DB_P13_FIELD_NAME in row, \
            "The given row with id %d does not contain a `%s` probability factor!" % (
                row[self.DB_ID_FIELD_NAME], self.DB_P13_FIELD_NAME
            )

        #
        # check and set values
        #

        self._map_int(row, self.DB_ID_FIELD_NAME)
        self._map_float(row, self.DB_P13_FIELD_NAME, 0, 100)

        probe_names = (
            self.DB_P31_FIELD_NAME,
            self.DB_P32_FIELD_NAME,
            self.DB_P23_FIELD_NAME,
            self.DB_P14_FIELD_NAME
        )

        is_probe_expected = True
        for probe_name in probe_names:
            if probe_name in row:
                assert is_probe_expected, "A probability value `%s` was given, although it was not expected: %s" % (
                    probe_name, row
                )
                self._map_float(row, probe_name, 0, 100)
            else:
                is_probe_expected = False


class TrafficControlManipulatorGeModelResource(DbHandler, MetaConfigInterface):
    """

    """

    DB_TABLE_NAME = 'gemodel'

    DB_ID_FIELD_NAME = 'id'
    DB_BAD_PROB_FIELD_NAME = 'p'
    DB_GOOD_PROB_FIELD_NAME = 'r'
    DB_GOOD_LOSS_PROB_FIELD_NAME = '1-h'
    DB_BAD_LOSS_PROB_FIELD_NAME = '1-k'

    _valid_field_names = (
        DB_ID_FIELD_NAME,
        DB_BAD_PROB_FIELD_NAME,
        DB_GOOD_PROB_FIELD_NAME,
        DB_GOOD_LOSS_PROB_FIELD_NAME,
        DB_BAD_LOSS_PROB_FIELD_NAME
    )

    @staticmethod
    def get_meta_description():
        from metaConfig.metaTable import MetaTable
        from metaConfig.metaTableField import MetaTableField

        return MetaTable(
            TrafficControlManipulatorGeModelResource.DB_TABLE_NAME,
            header_doc="""In this file you are able to configure arbitrary data sets og gilbert-elliot or bernoulli
models which can be used by the tc tool to manipulate the network traffic according to these models.""",
            fields=[
                MetaTableField(
                    TrafficControlManipulatorGeModelResource.DB_ID_FIELD_NAME,
                    int,
                    'unique id to identify the data set'
                ),
                MetaTableField(
                    TrafficControlManipulatorGeModelResource.DB_BAD_PROB_FIELD_NAME,
                    float,
                    'transition probability in % for bad states'
                ),
                MetaTableField(
                    TrafficControlManipulatorGeModelResource.DB_GOOD_PROB_FIELD_NAME,
                    float,
                    'the transition probability for good states [default: %s = 100%% - %s]' % (
                        TrafficControlManipulatorGeModelResource.DB_GOOD_PROB_FIELD_NAME,
                        TrafficControlManipulatorGeModelResource.DB_BAD_PROB_FIELD_NAME
                    )
                ),
                MetaTableField(
                    TrafficControlManipulatorGeModelResource.DB_GOOD_LOSS_PROB_FIELD_NAME,
                    float,
                    'loss probability in the good state [default: 0%]'
                ),
                MetaTableField(
                    TrafficControlManipulatorGeModelResource.DB_BAD_LOSS_PROB_FIELD_NAME,
                    float,
                    'loss probability in the bad state [default: 100%]'
                )
            ],
            footer_doc="""* If only %s is set             => Bernoulli Model
* If only %s and %s are set      => Simple Gilbert Model
* If only %s, %s and %s are set => Gilbert Model
* If all params set            => Gilbert-Elliot Model""" % (
                TrafficControlManipulatorGeModelResource.DB_BAD_PROB_FIELD_NAME,

                TrafficControlManipulatorGeModelResource.DB_BAD_PROB_FIELD_NAME,
                TrafficControlManipulatorGeModelResource.DB_GOOD_PROB_FIELD_NAME,

                TrafficControlManipulatorGeModelResource.DB_BAD_PROB_FIELD_NAME,
                TrafficControlManipulatorGeModelResource.DB_GOOD_PROB_FIELD_NAME,
                TrafficControlManipulatorGeModelResource.DB_GOOD_LOSS_PROB_FIELD_NAME
            )
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

        assert self.DB_ID_FIELD_NAME in row, \
            "The given row [%s] does not contain an id field!" % row

        assert self.DB_BAD_PROB_FIELD_NAME in row, \
            "The given row with id %d does not contain a `%s` probability factor!" % (
                row[self.DB_ID_FIELD_NAME], self.DB_BAD_PROB_FIELD_NAME
            )

        #
        # check and set values
        #

        self._map_int(row, self.DB_ID_FIELD_NAME)
        self._map_float(row, self.DB_BAD_PROB_FIELD_NAME, 0, 100)

        if self.DB_GOOD_PROB_FIELD_NAME in row:
            self._map_float(row, self.DB_GOOD_PROB_FIELD_NAME, 0, 100)

        if self.DB_GOOD_LOSS_PROB_FIELD_NAME in row:
            self._map_float(row, self.DB_GOOD_LOSS_PROB_FIELD_NAME, 0, 100)

        if self.DB_BAD_LOSS_PROB_FIELD_NAME in row:
            self._map_float(row, self.DB_BAD_LOSS_PROB_FIELD_NAME, 0, 100)