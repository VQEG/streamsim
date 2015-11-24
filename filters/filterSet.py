__author__ = 'Alexander Dethof'


class FilterSet:
    """
    This class represents a set of filters which have been set by the user.
    """

    # the delimiter which is used to separate a filter key from its value
    FILTER_KEY_VALUE_DELIMITER = '='

    # the delimiter which is used to separate a filter group from a filter key
    FILTER_GROUP_KEY_DELIMITER = '.'

    def __init__(self, filter_segments):
        """
        Main initialization of the filter set class: Sets ups the class' global variables and parses the given filter
         segments into a better representative data structure.

        :param filter_segments: the filter segments defined by user input,
            sample: ['group1.key1=value1', 'group2.key2=value2', ..., 'groupN.keyN=valueN']
        :type filter_segments: basestring[]
        """

        assert isinstance(filter_segments, list)

        self.__groups = dict()
        self.__parse_filter_segments(filter_segments)

    def __parse_filter_segments(self, filter_segments):
        """
        Parses the filter segments into a representative data structure.

        :param filter_segments: the filter segments defined by user input,
            sample: ['group1.key1=value1', 'group2.key2=value2', ..., 'groupN.keyN=valueN']
        :type filter_segments: basestring[]
        """

        assert isinstance(filter_segments, list)

        for filter_segment in filter_segments:
            assert isinstance(filter_segment, basestring)

            filter_elements = filter_segment.split(self.FILTER_KEY_VALUE_DELIMITER)
            assert isinstance(filter_elements, list)

            if len(filter_elements) == 2:
                (filter_key, filter_value) = filter_elements

                assert isinstance(filter_key, basestring)
                assert isinstance(filter_value, basestring)

                filter_key_elements = filter_key.split('.')
                assert isinstance(filter_key_elements, list)
                assert len(filter_key_elements) >= 2

                filter_key_elements.reverse()

                resource = self.__groups
                while filter_key_elements:
                    filter_key = filter_key_elements.pop()
                    if filter_key not in resource:
                        resource[filter_key] = dict()
                    if not filter_key_elements:
                        resource[filter_key] = filter_value
                    resource = resource[filter_key]

    def get_filter_group(self, group_id):
        """
        Returns all filters specified for a given filter group.
        NOTE: if the given group is not set in the filter set, an empty dictionary will be returned, in order
            to provide data consistency.

        :param group_id: the group id to look the filter settings for
        :type group_id: basestring

        :return: A dictionary with filters for the given group id
        :rtype: dict
        """

        assert isinstance(group_id, basestring)

        if group_id in self.__groups:
            return self.__groups[group_id]

        return dict()

    def get_filter_value(self, key, group_id):
        """
        Returns the filter value for a given filter key and group.
        NOTE: If no value is found, None is returned in order to keep the data consistency!

        :param key: the key to look up the filter value for
        :type key: basestring

        :param group_id: the group in which the key should be looked up
        :type group_id: basestring

        :return: the value for the filter or None, if nothing was found
        :rtype: basestring|None
        """

        assert isinstance(key, basestring)
        assert isinstance(group_id, basestring)

        group = self.get_filter_group(group_id)
        if key in group:
            return group[key]

        return None

    def __str__(self):
        """
        Returns a readable string of all filters, which where set in this instance. (useful for debugging)

        :return: A readable string of all filters, which where set in this instance.
        :rtype: basestring
        """

        return str(self.__groups)