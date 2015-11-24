__author__ = 'Alexander Dethof'


class Command:
    """
    This class can be used to build a command which can be executed on the command line.
    """

    # fields defining an argument
    ARG_FIELD_TYPE = 'type'
    ARG_FIELD_VALUE = 'value'
    ARG_FIELD_NAME = 'name'

    # types of parameters which can be set in this implementation
    COMMAND_GNU_CONV_PARAM = 'gnu-param'
    COMMAND_POSIX_CONV_PARAM = 'posix-param'
    COMMAND_TEXT_ARGUMENT = 'arg'

    def __init__(self, program_path):
        """
        Initialization of the command, which should run a given program.
        :param program_path: the full path (incl. name) of the program to execute on the command line
        """

        self.__is_subprocess = False
        self.__field_id_count = 0

        self.__argument_definitions = dict()
        self.__name_2_id_mappings = dict()

        self.__program_path = program_path
        self.__log_file_path = ''
        self.__is_std_err_redirect_to_file = False
        self.__is_std_err_redirect_to_std_out = False
        self.__tee = ()
        self.__stdin_file = None

    def __set(self, type_name, name, value=None):
        """
        Adds a parameter to the command instance.

        :param type_name: specifies the parameter's type -> necessary to print it out later in a command string
        :type type_name: basestring

        :param name: specfies the parameter's name, which is printed later
        :type name: basestring

        :param value: an optional value which can be set for the parameter
        :type value: None|basestring|int|float
        """

        assert isinstance(type_name, basestring)
        assert type_name in (self.COMMAND_GNU_CONV_PARAM, self.COMMAND_POSIX_CONV_PARAM, self.COMMAND_TEXT_ARGUMENT)

        assert isinstance(name, basestring)

        assert value is None \
               or isinstance(value, basestring) \
               or isinstance(value, int) \
               or isinstance(value, float)

        argument_definition = {
            self.ARG_FIELD_TYPE: type_name,
            self.ARG_FIELD_NAME: name,
            self.ARG_FIELD_VALUE: value
        }

        if name in self.__name_2_id_mappings:
            self.__argument_definitions[self.__name_2_id_mappings[name]] = argument_definition
        else:
            self.__argument_definitions[self.__field_id_count] = argument_definition
            self.__name_2_id_mappings[name] = self.__field_id_count

        self.__field_id_count += 1

    def is_subprocess(self):
        """
        Returns true if the command should be run as subprocess, false otherwise.

        :return: true if the command should be run as subprocess, false otherwise.
        :rtype: bool
        """

        return self.__is_subprocess

    def set_as_subprocess(self, is_subprocess=True):
        """
        Sets if the command should be run as subprocess or not.

        :param is_subprocess: true if the command should be run as subprocess, false otherwis
        :type is_subprocess: bool

        :return: self
        :rtype: Command
        """

        assert isinstance(is_subprocess, bool)

        self.__is_subprocess = is_subprocess

        return self

    def set_as_posix_option(self, param_name, param_value=None):
        """
        Sets a param with argument in the command. It will be shown as the following: -<PARAM_NAME> [<PARAM_VALUE>]
        Note that <PARAM_NAME> should be only one letter according to the posix "standard"

        :param param_name: the name of the param
        :type param_name: basestring

        :param param_value: the value of the param
        :type param_value: object|None

        :return: self
        :rtype: Command
        """

        self.__set(self.COMMAND_POSIX_CONV_PARAM, param_name, param_value)
        return self

    def set_as_gnu_option(self, param_name, param_value=None):
        """
        Sets a param with argument in the command. It will be shown as the following: --<PARAM_NAME> [<PARAM_VALUE>]
        Note that <PARAM_NAME> should be only one letter according to the gnu getopt "standard"

        :param param_name: the name of the param
        :type param_name: basestring

        :param param_value: the value of the param
        :type param_value: object|None

        :return: self
        :rtype: Command
        """

        self.__set(self.COMMAND_GNU_CONV_PARAM, param_name, param_value)
        return self

    def set_as_argument(self, arg_id, arg_text):
        """
        Sets further text to the command, which will be displayed as it is given.

        :param arg_id: a unique id which can be used to identify the text for later changes
        :type arg_id: basestring

        :param arg_text: the text to add to the command
        :type arg_text; basestring

        :return: self
        :rtype: Command
        """

        self.__set(self.COMMAND_TEXT_ARGUMENT, arg_id, arg_text)
        return self

    def set_as_log_file(self, file_path):
        """
        Sets a path where the output of the command can be logged

        :param file_path: the path to log the output in
        :type file_path: basestring

        :return: self
        :rtype: Command
        """

        assert isinstance(file_path, basestring)
        self.__log_file_path = file_path

        return self

    def set_std_err_redirect_to_file(self, redirect=True):
        """
        Redirects the output of the command from std_err to file

        :param redirect: True if the output has to be redirected from std_err to file, False otherwise
        :type redirect: bool

        :return: self
        :rtype: Command
        """

        self.__is_std_err_redirect_to_file = redirect
        return self

    def set_std_err_redirect_to_std_out(self, redirect=True):
        """
        Redirects the output of the command from std_err to std_out

        :param redirect: True if the output has to be redirected from std_err to std_out. False otherwise
        :type redirect: bool

        :return: self
        :rtype: Command
        """

        self.__is_std_err_redirect_to_std_out = redirect
        return self

    def tee(self, command, pipe=''):
        """
        Enables the command to be run with tee.

        :param command: the command to execute with tee
        :type command: basestring|Command

        :param pipe: the pipe's following commands
        :type pipe: basestring|Command

        :return: self
        :rtype: Command
        """

        assert isinstance(command, basestring) or isinstance(command, Command)
        assert isinstance(pipe, basestring) or isinstance(pipe, Command)

        self.__tee = (command, pipe)

    def file_to_stdin(self, file_path):
        """
        Adds a file which can be used as input parameter for the command.

        :param file_path: The path of the file to use as stdin
        :type file_path: basestring
        """

        assert isinstance(file_path, basestring)

        from os.path import isfile
        assert isfile(file_path)

        self.__stdin_file = file_path

    def __convert_argument_to_string(self, argument_definition):
        """
        Returns a string representation of a given command parameter set according to it's type.

        :param argument_definition: the definition of the argument's representation
        :return: a string representation of a given command parameter set according to it's type
        :rtype: basestring
        """

        assert isinstance(argument_definition, dict)
        assert self.ARG_FIELD_TYPE in argument_definition
        assert self.ARG_FIELD_NAME in argument_definition
        assert self.ARG_FIELD_VALUE in argument_definition

        type_name = argument_definition[self.ARG_FIELD_TYPE]

        name = argument_definition[self.ARG_FIELD_NAME]
        assert isinstance(name, basestring)

        value = argument_definition[self.ARG_FIELD_VALUE]

        if type_name == self.COMMAND_TEXT_ARGUMENT:
            return str(value)

        if type_name == self.COMMAND_POSIX_CONV_PARAM:
            if value is None:
                return "-%s" % name
            else:
                return "-%s %s" % (name, str(value))

        if type_name == self.COMMAND_GNU_CONV_PARAM:
            if value is None:
                return "--%s" % name
            else:
                return "--%s %s" % (name, str(value))

        raise KeyError('The could not be a string representation built for type `%s`' % type_name)

    def remove_arg(self, name):
        """
        Removes an argument which has been set previously in this command by its identifying name.

        :param name: name which defines the argument to remove
        :type name: basestring

        :return: self
        :rtype: Command
        """

        if name in self.__name_2_id_mappings:
            argument_id = self.__name_2_id_mappings[name]
            del self.__name_2_id_mappings[name]
            del self.__argument_definitions[argument_id]

        return self

    def __str__(self):
        """
        Returns the command - ready for the command line

        :return: the command - ready for the command line
        :rtype: basestring
        """

        argument_definitions = self.__argument_definitions.values()

        # build general command string by argument definitions
        command_string = "%s %s" % (self.__program_path, ' '.join(
            map(lambda argument_definition: self.__convert_argument_to_string(argument_definition),
                argument_definitions)))

        if self.__is_std_err_redirect_to_std_out:
            command_string += " 2>&1"

        if self.__tee:
            command_string += ' | tee ' + str(self.__tee[0])
            if self.__tee[1]:
                command_string += ' | ' + str(self.__tee[1])

        if self.__stdin_file is not None:
            command_string += ' < ' + self.__stdin_file

        # add log path if available
        if self.__log_file_path:
            command_string += ' '
            if self.__is_std_err_redirect_to_file:
                command_string += '2'
            command_string += '> ' + self.__log_file_path

        return command_string