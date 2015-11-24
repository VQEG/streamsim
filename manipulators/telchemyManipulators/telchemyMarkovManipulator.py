__author__ = 'Alexander Dethof'

from cmd.command import Command
from abstractTelchemyManipulator import AbstractTelchemyManipulator
# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR

from manipulators.resources.telchemyManipulatorResource import \
    TelchemyManipulatorMarkovResource as TelchemyMarkovRes, \
    TelchemyManipulatorMarkov2StateResource as Markov2StateRes, \
    TelchemyManipulatorMarkov4StateResource as Markov4StateRes, \
    TelchemyManipulatorMarkovPNamsPNBams4StateResource as MarkovPNamsPNBams4StateRes


class TelchemyMarkovManipulator(AbstractTelchemyManipulator):
    """
    Class to represent a manipulator which focuses on the manipulation with telchemy and markov models.
    """

    def __init__(self, parent, manipulator_settings_id, config_path):
        """
        Creates the manipulator for markov manipulation.

        :param parent: The parent which invoked the creation
        :type parent: manipulators.telchemyManipulator.TelchemyManipulator

        :param manipulator_settings_id: the id of the settings to manipulate for
        :type manipulator_settings_id: int

        :param config_path: the path where the config is located
        :type config_path: basestring
        """

        self.MANIPULATOR_RESOURCE_PATH = parent.MANIPULATOR_RESOURCE_PATH + PATH_SEPARATOR + 'markov'

        super(TelchemyMarkovManipulator, self).__init__(parent, manipulator_settings_id, config_path)

        self.__is_markov_2_state = False
        self.__is_markov_4_state = False
        self.__is_markov_pnamspbnams_4_state = False

        self.__model_settings = dict()

    def _get_resource_handler(self):
        """
        Returns the telchemy manipulator resource handler

        :return: The telchemy manipulator resource handler
        """

        return TelchemyMarkovRes(self._config_path + self.MANIPULATOR_RESOURCE_PATH)

    def __set_markov_model(self, markov_type):
        """
        Sets which markov model should be used by the manipulator.

        :param markov_type: Name of the markov model to use.
        :type markov_type: basestring
        """

        assert isinstance(markov_type, basestring)

        if markov_type == '2s':  # 2-state markov model
            self.__is_markov_2_state = True

        elif markov_type == '4s': # 4-state markov model
            self.__is_markov_4_state = True

        elif markov_type == 'p4':  # P.NAMS/P.NBAMS 4-state markov model
            self.__is_markov_pnamspbnams_4_state = True

        else:
            raise KeyError('Could not configure the Telchemy manipulator for the `%s`-model' % markov_type)

    def __get_markov_settings(self, markov_type, markov_id):
        """
        Returns the markovs settings which apply to the given model criteria.

        :param markov_type; The markov type to get the settings for
        :type markov_type: basestring

        :param markov_id: the id in the markov type table to load
        :type markov_id: int

        :return: The settings for the applied markov model
        :rtype: dict
        """

        assert isinstance(markov_type, basestring)
        assert isinstance(markov_id, int)

        resource = None
        if self.__is_markov_2_state:
            resource = Markov2StateRes(
                self._config_path + self.MANIPULATOR_RESOURCE_PATH + PATH_SEPARATOR + 'markov2state'
            )

        elif self.__is_markov_4_state:
            resource = Markov4StateRes(
                self._config_path + self.MANIPULATOR_RESOURCE_PATH + PATH_SEPARATOR + 'markov4state'
            )

        elif self.__is_markov_pnamspbnams_4_state:
            resource = MarkovPNamsPNBams4StateRes(
                self._config_path + self.MANIPULATOR_RESOURCE_PATH + PATH_SEPARATOR + 'pnamspnbams4'
            )

        if resource is None:
            raise KeyError('The given markov_type: `%s` is not registered in the telchemy manipulator!' % markov_type)

        return resource.get_row_with_id(markov_id)

    def __apply_markov_2_state_model(self, telchemy_command):
        """
        Applies the markov 2-state model to the given telchemy command.

        :param telchemy_command: The command to modify
        :type telchemy_command: Command
        """

        assert isinstance(telchemy_command, Command)
        assert isinstance(self.__model_settings, dict)

        telchemy_command.set_as_posix_option('pcb', float(self.__model_settings[Markov2StateRes.DB_FIELD_PCB]) / 100) \
                        .set_as_posix_option('pbc', float(self.__model_settings[Markov2StateRes.DB_FIELD_PBC]) / 100) \
                        .set_as_posix_option('g', float(self.__model_settings[Markov2StateRes.DB_FIELD_G]) / 100) \
                        .set_as_posix_option('b', float(self.__model_settings[Markov2StateRes.DB_FIELD_B]) / 100)

    def __apply_markov_4_state_model(self, telchemy_command):
        """
        Applies the markov 4-state model to the given telchemy command.

        :param telchemy_command: The command to modify
        :type telchemy_command: Command
        """

        assert isinstance(telchemy_command, Command)
        assert isinstance(self.__model_settings, dict)

        telchemy_command.set_as_posix_option('pba', float(self.__model_settings[Markov4StateRes.DB_FIELD_PBA]) / 100) \
                        .set_as_posix_option('pbc', float(self.__model_settings[Markov4StateRes.DB_FIELD_PBA]) / 100)

        if Markov4StateRes.DB_FIELD_PDC in self.__model_settings:
            telchemy_command.set_as_posix_option('pdc', float(self.__model_settings[Markov4StateRes.DB_FIELD_PDC]) / 100)

        if Markov4StateRes.DB_FIELD_PCD in self.__model_settings:
            telchemy_command.set_as_posix_option('pcd', float(self.__model_settings[Markov4StateRes.DB_FIELD_PCD]) / 100)

        if Markov4StateRes.DB_FIELD_PCB in self.__model_settings:
            telchemy_command.set_as_posix_option('pcb', float(self.__model_settings[Markov4StateRes.DB_FIELD_PCB]) / 100)

        telchemy_command.set_as_posix_option('g', float(self.__model_settings[Markov4StateRes.DB_FIELD_G]) / 100) \
                        .set_as_posix_option('b', float(self.__model_settings[Markov4StateRes.DB_FIELD_B]) / 100)

    def __apply_markov_pnamspbnams_4_state_model(self, telchemy_command):
        """
        Applies the markov P.NAMS/P.BNAMS model to the given telchemy command.

        :param telchemy_command: The command to modify
        :type telchemy_command: Command
        """

        assert isinstance(telchemy_command, Command)
        assert isinstance(self.__model_settings, dict)

        telchemy_command.set_as_posix_option(
            'loss_ratio', '%f' % (float(self.__model_settings[MarkovPNamsPNBams4StateRes.DB_FIELD_LOSS_RATIO]) / 100)
        ) \
                        .set_as_posix_option(
            'gap_ratio', '%f' % (float(self.__model_settings[MarkovPNamsPNBams4StateRes.DB_FIELD_GAP_RATIO]) / 100)
        )

    def __get_base_telchemy_command(self):
        """
        Returns a basic telchemy command, which can be used for further specifications.

        :return: A basic telchemy command, which can be used for further specifications
        :rtype: Command
        """

        telchemy_command = Command(self._parent.MANIPULATOR_PROGRAM_PATH)

        # specify markov model | NOTE: the P.NAMS/P.BNAMS model is not specified in here!
        if self.__is_markov_2_state:
            telchemy_command.set_as_posix_option('m', 2)
        elif self.__is_markov_4_state:
            telchemy_command.set_as_posix_option('m', 4)

        # specify loss insertion start time
        telchemy_command.set_as_posix_option('s', self._settings[TelchemyMarkovRes.DB_FIELD_START_AFTER])

        # specify loss insertion end time
        telchemy_command.set_as_posix_option('e', self._settings[TelchemyMarkovRes.DB_FIELD_END_BEFORE])

        return telchemy_command

    def set_telchemy_command_trace_store_option(self, telchemy_command):
        """
        Sets if the manipulations done with telchemy should be stored in a separate file.

        :param telchemy_command: the command to configure
        :type telchemy_command: Command
        """

        if not self._is_loss_trace_enabled:
            return

        trace_file_path = self._get_trace_file_path()

        from os.path import exists
        if exists(trace_file_path) and not self._is_override_mode:
            from os.path import basename
            print "# \033[95m\033[1m[TRACE] SKIP %s" % basename(trace_file_path)
            return

        telchemy_command.set_as_posix_option('c', trace_file_path)

    def __apply_markov_model(self):
        """
        Applies the markov model for the manipulator's settings on a basic telchemy command.
        """

        telchemy_command = self.__get_base_telchemy_command()

        if self.__is_markov_2_state:
            self.__apply_markov_2_state_model(telchemy_command)

        elif self.__is_markov_4_state:
            self.__apply_markov_4_state_model(telchemy_command)

        elif self.__is_markov_pnamspbnams_4_state:
            self.__apply_markov_pnamspbnams_4_state_model(telchemy_command)

        else:
            raise KeyError('The Telchemy manipulator has not a valid model to apply the settings on!')

        # finalize telchemy command with input and output file paths
        self._set_telchemy_command_file_input_output_options(telchemy_command)

        # if enabled add a loss trace option
        self.set_telchemy_command_trace_store_option(telchemy_command)

        # set loggings
        if self._log_folder and self._log_suffix:
            telchemy_log_file_path = self._get_log_file_path('telchemy')
            telchemy_command.set_as_log_file(telchemy_log_file_path)

        self._cmd(telchemy_command)

    def manipulate(self):
        """
        Performs the markov manipulation according to the manipulator's settings.
        """

        markov_type = self._settings[TelchemyMarkovRes.DB_FIELD_MARKOV_TYPE]
        self.__set_markov_model(markov_type)

        markov_id = int(self._settings[TelchemyMarkovRes.DB_FIELD_MARKOV_ID])
        self.__model_settings = self.__get_markov_settings(markov_type, markov_id)

        self.__apply_markov_model()