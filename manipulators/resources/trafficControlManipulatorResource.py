__author__ = 'Alexander Dethof'

from database.dbHandler import DbHandler


class TrafficControlManipulatorResource(DbHandler):
    """

    """

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


class TrafficControlManipulatorRandomModeResource(DbHandler):
    """

    """

    DB_ID_FIELD_NAME = 'id'
    DB_LOSS_RATE_FIELD_NAME = 'loss_rate'

    _valid_field_names = (
        DB_ID_FIELD_NAME,
        DB_LOSS_RATE_FIELD_NAME
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


class TrafficControlManipulatorStateModeResource(DbHandler):
    """

    """

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


class TrafficControlManipulatorGeModelResource(DbHandler):
    """

    """

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