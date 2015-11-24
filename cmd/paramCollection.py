__author__ = 'Alexander Dethof'


class ParamCollection:
    """
    This class can be used to build a chain of many parameters which can be converted than to a string and added into
    a command which can be executed.

    The conversion for N param-value pairs will look like the following scheme:

    `param1=value1:param2=value2:...paramN=valueN`
    """

    def __init__(self):
        """
        Initialization of a new param collection.
        """

        self.__params = dict()

    def set(self, key, value):
        """
        Sets/overrides a new key value pair in the collection
        :param key: name of the parameter
        :param value: the value configuring the parameter
        """

        self.__params[key] = value

        return self

    def __len__(self):
        """
        Returns the length of the collection's params
        :return: the length of the collection's params
        """

        return len(self.__params)

    def __str__(self):
        """
        Returns the collection converted as a string in the following scheme for N param-value pairs:

        `param1=value1:param2=value2:...paramN=valueN`

        :return: the collection converted as a string in the following scheme for N param-value pairs:

        `param1=value1:param2=value2:...paramN=valueN`
        """

        return ':'.join(['%s=%s' % (key, self.__params[key]) for key in self.__params.keys()])
