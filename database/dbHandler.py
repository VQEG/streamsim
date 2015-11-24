__author__ = 'Alexander Dethof'

from database.dbTable import DbTable
from abc import ABCMeta, abstractmethod


class DbHandler(object):
    """
    Represents a handler which can be used to extend interact directly with a data base table. The idea is that this
    class should never be initialized directly. It should be further more used as an abstract parent class for other
    classes for which it might be useful, that the functions which are callable on the database table are also
    callable on the extending class itself.
    """

    # the class is set as abstract class to ensure that it can not be created directly
    #  (would not make any sense otherwise)
    __metaclass__ = ABCMeta

    # defines a list of valid field names
    _valid_field_names = tuple()

    def __init__(self, db_table_path, id_field_name='id', filters=None):
        """
        Main initialization of the database handler, i.e. it will load the appropriate database table for the
        given table path.

        :param db_table_path: the path of the table to build the handler for
        :type db_table_path: basestring

        :param id_field_name: the name of the id field
        :type id_field_name: basestring

        :param filters: filters which can be set on the db tables
        :type filters: None|dict
        """

        # validate input arguments
        assert isinstance(db_table_path, basestring)
        assert isinstance(id_field_name, basestring)
        assert filters is None \
               or isinstance(filters, dict)

        # load csv table
        self.__table = DbTable(
            db_table_path,
            id_field_name,
            self._valid_field_names,
            filters,
            self.validate  # callback to validate the rows loaded
        )

    @staticmethod
    def _assert_fields(row, id_field_name, required_fields=()):
        """
        Checks if a row consists of the given id field and additional required fields. If one field could not be found
        an error occurs, else the row is valid!

        :param row: the row to assert
        :type row: dict

        :param id_field_name: the name of the field storing the row's id
        :type id_field_name: basestring

        :param required_fields: an optional list of additional fields, which are required
        :type required_fields: tuple|list
        """

        assert isinstance(row, dict)
        assert isinstance(id_field_name, basestring)
        assert id_field_name in row, \
            "The given row [%s] does not contain an id field!" % row


        for req_field in required_fields:
            assert isinstance(req_field, basestring)
            assert req_field in row, \
                "The given row with id `%s` does not contain a `%s` field value!" % (
                    row[id_field_name], req_field
                )

    def _map_int(self, row, key, min_val=None, max_val=None):
        """
        Maps a value of a given row at its key position to an integer value, if possible. Raises an error if not!

        :param row: The row where the value should be mapped to an int
        :type row: dict

        :param key: The key referencing the value to map
        :type key: tuple|list|basestring
        """

        assert isinstance(row, dict)

        if isinstance(key, tuple) or isinstance(key, list):
            keys = key
            for key in keys:
                if isinstance(key, tuple) or isinstance(key, list):
                    if len(key) == 1:
                        if min_val is None and max_val is None:
                            self._map_int(row, key[0], min_val, max_val)
                        elif max_val is None:
                            self._map_int(row, key[0], min_val)
                        else:
                            self._map_int(row, key[0])
                    elif len(key) == 2:
                        self._map_int(row, key[0], key[1])
                    elif len(key) == 3:
                        self._map_int(row, key[0], key[1], key[2])
                    else:
                        raise SyntaxError('Wrong number of arguments given: Got %d - Expected %d' % (len(key), 3))
                else:
                    self._map_int(row, key)
            return

        assert isinstance(row[key], basestring)
        assert row[key].isdigit()

        row[key] = int(row[key])

        if min_val is not None:
            self._map_min_value(row, key, min_val)

        if max_val is not None:
            self._map_max_value(row, key, max_val)

    def _map_float(self, row, key, min_val=None, max_val=None):
        """
        Maps a value of a given row at its key position to a float value, if possible. Raises an error if not!

        :param row: The row where the value should be mapped to a float
        :type row: dict

        :param key: The key referencing the value to map
        :type key: tuple|list|basestring
        """

        if isinstance(key, tuple) or isinstance(key, list):
            keys = key
            for key in keys:
                if isinstance(key, tuple) or isinstance(key, list):
                    if len(key) == 1:
                        if min_val is None and max_val is None:
                            self._map_float(row, key[0], min_val, max_val)
                        elif max_val is None:
                            self._map_float(row, key[0], min_val)
                        else:
                            self._map_float(row, key[0])
                    elif len(key) == 2:
                        self._map_float(row, key[0], key[1])
                    elif len(key) == 3:
                        self._map_float(row, key[0], key[1], key[2])
                    else:
                        raise SyntaxError('Wrong number of arguments given: Got %d - Expected %d' % (len(key), 3))
                else:
                    self._map_float(row, key)
            return

        assert isinstance(row[key], basestring)

        items = row[key].split('.')
        items_count = len(items)
        assert 1 <= items_count <= 2, "Invalid `%s`-value given - is not a float: %s" % (key, row)

        if items_count >= 1:
            assert isinstance(items[0], basestring)
            assert items[0].isdigit()

            row[key] = float(items[0])

        if items_count >= 2:
            assert isinstance(items[1], basestring)
            assert items[1].isdigit()

            row[key] = float(items[0] + '.' + items[1])

        if min_val is not None:
            self._map_min_value(row, key, min_val)

        if max_val is not None:
            self._map_max_value(row, key, max_val)

    @staticmethod
    def _map_val_range(row, key, valid_values):
        """
        Checks if a value of a given row at its key position is a value of a given value range. Raises an error if not!

        :param row: The row where the value should be checked
        :type row: dict

        :param key: The key referencing the value to check
        :type key: basestring

        :param valid_values: The values of which the value to check has to be a part of
        :type valid_values: list|tuple
        """

        assert isinstance(row, dict)
        assert isinstance(key, basestring)
        assert isinstance(valid_values, list) or isinstance(valid_values, tuple)

        assert row[key] in valid_values, \
            "The given `%s` value `%s` is not a value of the followings: %s" % (
                key,
                row[key],
                valid_values
            )

    @staticmethod
    def _map_min_value(row, key, min_val):
        """
        Checks if a given value is greater or equal a given numeric limit.

        :param row: the row to extract the value from
        :type row: dict

        :param key: the key referencing the value in the row
        :type key: basestring

        :param min_val: the limit the value has to be greater or equal
        :type min_val: int|float
        """

        assert isinstance(row, dict)
        assert isinstance(key, basestring)
        assert isinstance(min_val, int) or isinstance(min_val, float)

        assert isinstance(row[key], int) or isinstance(row[key], float)
        assert min_val <= row[key], "The given `%s`-value is smaller than %.2f: %s" % (key, min_val, row)

    @staticmethod
    def _map_max_value(row, key, max_val):
        """
        Checks if a given value is smaller or equal a given numeric limit.

        :param row: the row to extract the value from
        :type row: dict

        :param key: the key referencing the value in the row
        :type key: basestring

        :param max_val: the limit the value has to be smaller or equal
        :type max_val: int|float
        """

        assert isinstance(row, dict)
        assert isinstance(key, basestring)
        assert isinstance(max_val, int) or isinstance(max_val, float)

        assert isinstance(row[key], int) or isinstance(row[key], float)
        assert max_val >= row[key], "The given `%s`-value is greater than %.2f: %s" % (key, max_val, row)

    def _remove(self, data_set_id):
        """
        Removes a data set with a specified id from the table.

        :param data_set_id: the id of the data set to remove
        :type data_set_id: int
        """

        assert isinstance(data_set_id, int)
        self.__table.remove(data_set_id)

    def get_rows(self):
        """
        Returns all rows of the handler's table

        :return: all rows of the handler's table
        :rtype: list
        """

        return self.__table.get_rows()

    def is_filtered(self, data_set_id):
        """
        Returns true if the given id is usually part of this table but in this session it is filtered.

        :param data_set_id: the id to look the filter state for
        :type data_set_id: int

        :return: true if the given id is usually part of this table but in this session it is filtered; false otherwise.
        :rtype: bool
        """

        assert isinstance(data_set_id, int)
        return self.__table.is_filtered(data_set_id)

    def has_row_with_id(self, row_id):
        """
        Returns true if the handler's table has a row with the given id, false otherwise

        :param row_id: the id to look for in the handler's table's rows
        :type row_id: int

        :return: true if the handler's table has a row with the given id, false otherwise
        :rtype: bool
        """

        return self.__table.has_row_with_id(row_id)

    def get_row_with_id(self, row_id):
        """
        Returns a row of the handler's table with the given id.

        :param row_id: the id to return the row for
        :type row_id: int

        :return: a row of the handler's table with the given id
        :rtype: dict
        """

        return self.__table.get_row_with_id(row_id)

    @abstractmethod
    def validate(self, row):
        """
        Validates a given row if it is valid for the table configuration or not. (automatically called on creation)

        :param row: the row to validate
        :type row: dict

        :raise AssertionError: if an assertion failed during the validation
        """

        pass

    def __str__(self):
        """
        Returns a string representation of the handler's table. (useful for debugging)

        :return: a string representation of the handler's table
        :rtype: basestring
        """

        return str(self.__table)