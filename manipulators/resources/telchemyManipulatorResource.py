__author__ = 'Alexander Dethof'


from database.dbHandler import DbHandler


class TelchemyManipulatorResource(DbHandler):

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


class TelchemyManipulatorReadTraceResource(DbHandler):

    DB_FIELD_NAME_ID = 'id'
    DB_FIELD_NAME_TRACE_FILE_NAME = 'trace_file_name'

    _valid_field_names = (
        DB_FIELD_NAME_ID,
        DB_FIELD_NAME_TRACE_FILE_NAME
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


class TelchemyManipulatorMarkovResource(DbHandler):

    DB_FIELD_NAME_ID = 'id'
    DB_FIELD_MARKOV_TYPE = 'markov_type'
    DB_FIELD_MARKOV_ID = 'markov_id'
    DB_FIELD_START_AFTER = 'start_after'
    DB_FIELD_END_BEFORE = 'end_before'

    VALID_MARKOV_TYPES = (
        '2s',
        '4s',
        'p4',
        'r'
    )

    _valid_field_names = (
        DB_FIELD_NAME_ID,
        DB_FIELD_MARKOV_TYPE,
        DB_FIELD_MARKOV_ID,
        DB_FIELD_START_AFTER,
        DB_FIELD_END_BEFORE
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


class TelchemyManipulatorMarkov2StateResource(DbHandler):

    DB_FIELD_ID = 'id'
    DB_FIELD_PCB = 'pcb'
    DB_FIELD_PBC = 'pbc'
    DB_FIELD_G = 'g'
    DB_FIELD_B = 'b'

    _valid_field_names = (
        DB_FIELD_ID,
        DB_FIELD_PCB,
        DB_FIELD_PBC,
        DB_FIELD_G,
        DB_FIELD_B
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

        self._assert_fields(row, self.DB_FIELD_ID, (
            self.DB_FIELD_PCB,
            self.DB_FIELD_PBC,
            self.DB_FIELD_G,
            self.DB_FIELD_B
        ))

        #
        # check and set values
        #

        self._map_int(row, self.DB_FIELD_ID)
        self._map_float(row, (
            self.DB_FIELD_PCB,
            self.DB_FIELD_PBC,
            self.DB_FIELD_G,
            self.DB_FIELD_B
        ), 0, 100)


class TelchemyManipulatorMarkov4StateResource(DbHandler):

    DB_FIELD_ID = 'id'
    DB_FIELD_PBA = 'pba'
    DB_FIELD_PBC = 'pbc'
    DB_FIELD_PDC = 'pdc'
    DB_FIELD_PCD = 'pcd'
    DB_FIELD_PCB = 'pcb'
    DB_FIELD_G = 'g'
    DB_FIELD_B = 'b'

    _valid_field_names = (
        DB_FIELD_ID,
        DB_FIELD_PBA,
        DB_FIELD_PBC,
        DB_FIELD_PDC,
        DB_FIELD_PCD,
        DB_FIELD_PCB,
        DB_FIELD_G,
        DB_FIELD_B
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

        self._assert_fields(row, self.DB_FIELD_ID, (
            self.DB_FIELD_PBA,
            self.DB_FIELD_PBC,
            self.DB_FIELD_PDC,
            self.DB_FIELD_PCD,
            self.DB_FIELD_PCB,
            self.DB_FIELD_G,
            self.DB_FIELD_B
        ))

        #
        # check and set values
        #

        self._map_int(row, self.DB_FIELD_ID)
        self._map_float(row, (
            self.DB_FIELD_PBA,
            self.DB_FIELD_PBC,
            self.DB_FIELD_G,
            self.DB_FIELD_B
        ), 0, 100)

        if self.DB_FIELD_PDC in row:
            self._map_float(row, self.DB_FIELD_PDC, 0, 100)

        if self.DB_FIELD_PCD in row:
            self._map_float(row, self.DB_FIELD_PCD, 0, 100)

        if self.DB_FIELD_PCB in row:
            self._map_float(row, self.DB_FIELD_PCB, 0, 100)


class TelchemyManipulatorMarkovPNamsPNBams4StateResource(DbHandler):

    DB_FIELD_ID = 'id'
    DB_FIELD_LOSS_RATIO = 'loss_ratio'
    DB_FIELD_GAP_RATIO = 'gap_ratio'

    _valid_field_names = (
        DB_FIELD_ID,
        DB_FIELD_LOSS_RATIO,
        DB_FIELD_GAP_RATIO
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

        self._assert_fields(row, self.DB_FIELD_ID, (
            self.DB_FIELD_LOSS_RATIO,
            self.DB_FIELD_GAP_RATIO
        ))

        #
        # check and set values
        #

        self._map_int(row, self.DB_FIELD_ID)
        self._map_float(row, (
            self.DB_FIELD_LOSS_RATIO,
            self.DB_FIELD_GAP_RATIO
        ), 0, 100)