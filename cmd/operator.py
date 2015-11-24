__author__ = 'Alexander Dethof'

from command import Command
from cmd.commandCollection import CommandCollection
from multiprocessing import Process
from signal import SIGTERM
from os import killpg, getpgid, setsid, system

CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


class Operator(object):
    """
    This class is able to operate with the command line. It can log errors and warnings, but also execute commands.
    This command execution can be simulated in a dry-run mode.
    """

    # True if the tool should be run dry; False otherwise
    _is_dry_run = True

    def __init__(self):
        """
        Initialization of the operator. Checks if the class has been configured correctly.
        """

        assert isinstance(self._is_dry_run, bool)

    @staticmethod
    def log_event(etype, e):
        """
        Logs an event to the command line of a specific event type.

        :param etype: the event type's name
        :type etype: basestring

        :param e: the event to log
        :type e: object
        """

        assert isinstance(etype, basestring)
        assert isinstance(e, object)

        print '# %s: %s' % (etype, e)

    @staticmethod
    def _log_warning(w):
        """
        Logs a given warning to the command line

        :param w: the warning to log
        :type w: Warning
        """

        assert isinstance(w, Warning)
        Operator.log_event('\033[1m\033[93mWarning\033[0m', w)

    @staticmethod
    def _log_exception(e):
        """
        Logs a given exception to the command line

        :param e: the exception to log
        :type e: Exception
        """

        assert isinstance(e, Exception)
        Operator.log_event('\033[1m\033[91mException\033[0m', e)

    def set_dry_mode(self, is_dry):
        """
        Manipulates the class behaviour to work in dry mode or not
        
        :param is_dry: true if the class should work in dry mode; false otherwise
        :type is_dry: bool
        """

        assert isinstance(is_dry, bool)

        self._is_dry_run = is_dry

        return self

    @staticmethod
    def _terminate_process_with_children(process, signal=SIGTERM):
        """
        Terminates a given process with all its children cleanly.

        :param process: the process to terminate with all its children
        :type process: Process

        :param signal: signal to send to the children processes to terminate (SIGTERM by default)
        :type signal: int
        """

        assert isinstance(process, Process)

        if not process.is_alive():
            return

        pgid = getpgid(int(process.pid))
        killpg(pgid, signal)

    @staticmethod
    def __execute_command_in_new_session(command):
        """
        Executes a command in a new session, this will enable to separately kill the command from the main application

        :param command: The command to execute in an external session
        """

        setsid()
        system(command)

    @staticmethod
    def _remove_last_output():
        """
        Removes the last output done in stdout
        """

        print(CURSOR_UP_ONE + ERASE_LINE + CURSOR_UP_ONE)

    def _cmd(self, command, auto_start=True):
        """
        If the class is set in dry mode this method will print the given command, otherwise it will be executed
        on the command line. If the given command should be run in background mode it will be executed in a new
        subprocess. In this case the subprocess will be returned, otherwise none.

        <strong style="text-decoration:underline;color:#a00">ATTENTION!!</strong> Please be aware if a command will
         be executed in background mode, your are responsible to terminate the returned process afterwards!

        :type command: Command|CommandCollection
        :type auto_start: bool

        :param command: the command to executed
        :param auto_start: true if the process should start automatically (if subprocess), false otherwise

        :return: the subprocess created for this command or none if the command should be executed directly
        """

        # validate inputs
        assert isinstance(command, Command) or isinstance(command, CommandCollection)
        assert isinstance(auto_start, bool)

        # get and print command which should be executed on the command line
        cmd_str = str(command)
        print '# \033[1m\033[94mRUN : %s\033[0m' % cmd_str

        # if the operator should not be run dry -> execute the command
        if not self._is_dry_run:

            # if the tool should be executed in background a new subprocess will be executed to run the command
            # and returned
            if command.is_subprocess():
                pargs = list()
                pargs.append(cmd_str)

                process = Process(target=self.__execute_command_in_new_session, args=pargs)

                if auto_start:
                    process.start()

                return process

            # otherwise the command will be run directly
            else:
                system(cmd_str)

        # If no subprocess has been created or the command ran dry - no subprocess will be returned!
        return None
