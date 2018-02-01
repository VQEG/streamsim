__author__ = 'Alexander Dethof'

from csv import reader
import os


class DbTable:
    """
    This class represents a table which stores data. The programming style forces to abstract the table from it's
    underlying base. Currently this table works for .csv-files, but can be also converted to other database formats.
    """

    # the delimiter used in the .csv files
    DB_TABLE_COLUMN_DELIMITER = ';'

    # define filter parser access keys
    FILTER_PARSER_FILTER_MODE_KEY = 'filter_mode'
    FILTER_PARSER_FILTER_ELEM_KEY = 'filter_elem'

    # define filter modes
    FILTER_MODE_KEEP_ONLY = 'keep'
    FILTER_MODE_LEAVE_OUT = 'leave'

    def __init__(self, db_table_name, id_field_name, valid_field_names=tuple(), filters=None, validator=None):
        """
        Initializes the database table class, i.e. it loads the data of the table into the internal data structure, so
        that it can be read easily in further applications.

        :param db_table_name: the name of the table
        :type db_table_name: basestring

        :param id_field_name: the name of the field containing the table's entries' id
        :type id_field_name: basestring

        :param valid_field_names: a list containing the field names, which are allowed to be imported
        :type valid_field_names: list|tuple

        :param filters: filters which can be set on the table
        :type filters: None|dict

        :param validator: a callback to validate the rows loaded in the table
        :type validator: callback
        """
        if not filters:
            filters = dict()

        # init internal fields
        self.__field_names = dict()
        self.__id_reference_table = dict()
        self.__rows = list()

        # validate delimiter field
        assert isinstance(self.DB_TABLE_COLUMN_DELIMITER, basestring)

        # validate argument input
        assert isinstance(db_table_name, basestring)
        assert isinstance(id_field_name, basestring)
        assert isinstance(valid_field_names, tuple)
        assert isinstance(filters, dict)

        # configure csv table path and load the file
        self.__id_field_name = id_field_name
        self.__path = db_table_name + '.csv'
        self.__validator = validator

        self.__parse_filters(filters, valid_field_names)
        self.__load_db_table(valid_field_names)

    def __parse_filters(self, filters, valid_field_names):
        """
        Parses the given filters and stores them in an internal dictionary.

        :param filters: the filters to parse (given by user input)
        :type filters: dict

        :param valid_field_names: a list of valid field names which can be filtered
        :type valid_field_names: list|tuple
        """

        self.__filters = dict()
        self.__filtered_ids = list()

        assert isinstance(filters, dict)
        filter_items = filters.items()
        for (filter_key, filter_value) in filter_items:
            # check if the given filter value is parse-able and continue if not
            if not isinstance(filter_value, basestring):
                continue

            if filter_key == 'id':
                filter_key = self.__id_field_name

            if filter_key not in valid_field_names:
                raise KeyError('Unknown filter key given: `%s`' % filter_key)

            filter_mode = self.FILTER_MODE_KEEP_ONLY
            is_leave_out_filter = filter_value.startswith('-')
            if is_leave_out_filter:
                filter_value = filter_value.replace('-', '')
                filter_mode = self.FILTER_MODE_LEAVE_OUT

            self.__filters[filter_key] = {
                self.FILTER_PARSER_FILTER_MODE_KEY: filter_mode,
                self.FILTER_PARSER_FILTER_ELEM_KEY: filter_value.split(',')
            }

    def __load_db_table(self, valid_field_names):
        """
        This method loads the table's content into the internal data structures. Only the data from valid field names
        are imported. All other data is left out. The method expects the following table structure:

        <table>
            <thead>
                <tr><td>field_name_1</td><td>field_name_2</td><td>...</td><td>field_name_n</td></tr>
            </thead>
            <tbody>
                <tr><td>row_1:value_1</td><td>row_1:value_2</td><td>...</td><td>row_1:value_n</td></tr>
                <tr><td>row_2:value_1</td><td>row_2:value_2</td><td>...</td><td>row_2:value_n</td></tr>
                <tr><td colspan="4">...</td></tr>
                <tr><td>row_m:value_1</td><td>row_m:value_2</td><td>...</td><td>row_m:value_n</td></tr>
            </tbody>
        </table>

        :param valid_field_names: a list of field names of which the data is allowed to be imported
        :type valid_field_names: tuple
        """

        # assert input params
        assert isinstance(valid_field_names, tuple)

        # Assert that the name of the id field is in the valid field names list
        assert self.__id_field_name in valid_field_names

        # Assert that the given path is a valid file
        assert os.path.isfile(self.__path),\
            'The path `%s` is not a valid database table file!' % self.__path

        # Assert that the file at the given path is readable
        assert os.access(self.__path, os.R_OK)

        # Load the csv-file data into a csv reader ...
        csv_file = open(self.__path)
        csv_reader = reader(csv_file, delimiter=self.DB_TABLE_COLUMN_DELIMITER)

        is_header_row = True
        id_field_index = -1
        # ... and import it according to the expected structure
        for row in csv_reader:
            assert isinstance(row, list)

            # skip empty rows
            if len(row) == 0:
                continue

            # leave out commented lines
            if str(row[0]).startswith('#'):
                continue

            # evaluate the table's header row: import field names
            if is_header_row:
                field_name_index = 0
                for field_name in row:
                    if field_name in valid_field_names:
                        if field_name == self.__id_field_name:
                            id_field_index = field_name_index
                        self.__field_names[field_name_index] = field_name
                    field_name_index += 1

                is_header_row = False

                # if the id field was not imported, the data import aborts, due to the problem, that the data can not
                # be valid referenced
                if id_field_index == -1:
                    raise KeyError(
                        'The resource file `%s` does not contain the id field `%s` and could not be imported.' % (
                            self.__path,
                            self.__id_field_name
                        )
                    )

            # if the current row is not a header row it's data will be added to the table or filtered out
            else:
                data_set = dict()
                data_set_id = int(row[id_field_index])
                field_names = self.__field_names.items()

                row_count = len(row)
                is_filtered_data_set = False
                for (field_index, field_name) in field_names:
                    if field_index >= row_count:
                        break

                    data_value = row[field_index]
                    if field_name in self.__filters:
                        filter_set = self.__filters[field_name]
                        filter_mode = filter_set[self.FILTER_PARSER_FILTER_MODE_KEY]
                        filter_elem = filter_set[self.FILTER_PARSER_FILTER_ELEM_KEY]

                        if (filter_mode == self.FILTER_MODE_LEAVE_OUT
                                and data_value in filter_elem) \
                                or (filter_mode == self.FILTER_MODE_KEEP_ONLY
                                and data_value not in filter_elem):
                            is_filtered_data_set = True
                            break

                    data_set[field_name] = row[field_index]

                if is_filtered_data_set:
                    self.__filtered_ids.append(data_set_id)
                    print '# \x1b[33m\033[1mFILTER %s: id = %d\033[0m'\
                          % (self.__path, data_set_id)
                    continue

                # append only non-empty AND valid data!!
                filtered_row = dict(filter(lambda (k,v): not (not v), data_set.items()))
                self.__validate_row(filtered_row)

                # store data set and reference it's id in the lookup table
                self.__id_reference_table[data_set_id] = len(self.__rows)
                self.__rows.append(filtered_row)

    def check_valid_field_names(self, row):
        """
        Returns true if the given row is a dictionary which implements all fields which are also implemented in the
        table and is registered with the id in the table, false otherwise.

        :param row: the row to check to be a valid row from the table
        :type row: dict

        :return: true if the given row is a dictionary which implements all fields which are also implemented in the
        table and is registered with the id in the table, false otherwise.
        :rtype: bool
        """

        assert isinstance(row, dict)
        assert set(row.keys()).issubset(set(self.__field_names.values()))

    def __validate_row(self, row):
        """
        Validates a given row, if it contains only valid field names. If specified, an extra validation callback
        will be executed which can be used to further validate the row.

        NOTE: The method will not return a validation state, if it will not return an error, the row is valid, otherwise
            it is invalid!!

        :param row: the row to validate
        :type row: dict
        """

        self.check_valid_field_names(row)
        if self.__validator:
            self.__validator(row)

    def get_field_names(self):
        """
        Returns all names of the fields which are used in this table

        :return: all names of the fields which are used in this table
        :rtype: list
        """

        return self.__field_names

    def get_rows(self):
        """
        Returns all rows/data sets of the table

        :return: all rows/data sets of the table
        :rtype: dict[]
        """

        return self.__rows

    def get_column(self, col_name):
        """
        Returns the whole data which is stored for a specific table field

        :param col_name: the name of the table field to get the data for
        :type col_name: basestring

        :return: all data stored for the given table field
        :rtype: list
        """

        assert isinstance(col_name, basestring)

        return [row[col_name] for row in self.__rows]

    def get_row_at(self, index):
        """
        Returns the row which is stored at the given index number

        :param index: the index number to return a row for
        :type index: int

        :return: the row which is stored at the given index number
        :rtype: dict
        """

        assert isinstance(index, int)

        return self.__rows[index]

    def has_row_with_id(self, row_id):
        """
        Return true if there exists a row in the table with the given id, false otherwise.

        :param row_id: the id to look for
        :type row_id: int

        :return: true if there exists a row in the table with the given id, false otherwise
        :rtype: bool
        """

        assert isinstance(row_id, int)
        return row_id in self.__id_reference_table

    def get_row_with_id(self, row_id):
        """
        Returns the row which has the given row id.

        :param row_id: the id of the row to return for
        :type row_id: int

        :return: the row which has the given row id
        :rtype: dict

        :raises KeyError: if no data set with the given id exists in the table!
        """

        assert isinstance(row_id, int)

        try:
            return self.__rows[self.__id_reference_table[row_id]]
        except KeyError:
            raise KeyError('There was no data entry with id=%d found in table `%s`' % (row_id, self.__path))

    def is_filtered(self, data_set_id):
        """
        Returns true if the given id is usually part of this table but in this session it is filtered.

        :param data_set_id: the id to look the filter state for
        :type data_set_id: int

        :return: true if the given id is usually part of this table but in this session it is filtered; false otherwise.
        :rtype: bool
        """

        return data_set_id in self.__filtered_ids

    def remove(self, data_set_id):
        """
        Removes a row in the table with the given id and updates the id reference table.

        :param data_set_id: the id of the data set to remove
        :type data_set_id: int
        """

        assert isinstance(data_set_id, int)
        assert data_set_id in self.__id_reference_table

        del self.__rows[self.__id_reference_table[data_set_id]]

        # update the id reference table
        self.__id_reference_table = dict()
        row_count = len(self.__rows)
        for row_index in range(0, row_count):
            row = self.__rows[row_index]
            self.__id_reference_table[int(row[self.__id_field_name])] = row_index

    def __str__(self):
        """
        This function transforms the database table into a string representation which shows the name of all fields
        used and further more all rows.

        :return: a string representation which shows the name of all fields used and further more all rows
        :rtype: basestring
        """

        return '''TABLE %s

Fields (%d)
============
%s

Rows (%d)
==========
%s
''' % (self.__path, len(self.__field_names), self.__field_names, len(self.__rows), self.__rows)