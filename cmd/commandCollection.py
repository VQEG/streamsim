__author__ = 'Alexander Dethof'

from command import Command


class CommandCollection(object):
    """
    Generates a collection of commands which are allowed to be execute in parallel
    """

    def __init__(self, *commands):
        """
        Creates the command collection with all commands given as arguments

        :param commands: the commands to create the collection for
        :type commands: Command*
        """

        self.__commands = list(commands)
        self.__is_subprocess = False

    def add_command(self, command):
        """
        Adds a command to the collection

        :param command: the command to add
        :type command: Command
        """

        assert isinstance(command, Command)
        self.__commands.append(command)

    def set_as_subprocess(self, is_subprocess=True):
        """
        Sets the collection as subprocess or as single process (depending on the input argument)
        :param is_subprocess: true if the collection should be set as subprocess, false otherwise.
        :type is_subprocess: bool
        """

        assert isinstance(is_subprocess, bool)
        self.__is_subprocess = is_subprocess

    def is_subprocess(self):
        """
        Returns true if the collection is set as a subprocess; false otherwise.
        :return: true if the collection is set as a subprocess; false otherwise.
        """

        return self.__is_subprocess

    def __len__(self):
        """
        Returns the number of parallel executable commands
        :return: the number of parallel executable commands
        """

        return len(self.__commands)

    def __str__(self):
        """
        Returns a string which can be logged into the command line to execute all commands in parallel
        :return: a string which can be logged into the command line to execute all commands in parallel
        """

        return " && ".join(map(lambda command: str(command), self.__commands))