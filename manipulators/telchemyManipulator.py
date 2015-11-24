__author__ = 'Alexander Dethof'

# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR

from abstractManipulator import AbstractManipulator
from resources.telchemyManipulatorResource import TelchemyManipulatorResource as TelchemyRes


class TelchemyManipulator(AbstractManipulator):
    """
    Manipulation classes which uses the telchemy tpkloss tool in order to insert offline packet loss.
    """

    # path of the resource table to load wherein the manipulation is specified
    MANIPULATOR_RESOURCE_PATH = 'hrc' + PATH_SEPARATOR + 'packet_loss' + PATH_SEPARATOR + 'telchemy'

    # path of the program to use in order to invoke the packet manipulation
    MANIPULATOR_PROGRAM_PATH = 'tpkloss'

    def _get_resource_handler(self):
        """
        Returns the telchemy manipulator resource handler

        :return: The telchemy manipulator resource handler
        """

        return TelchemyRes(self._config_path + self.MANIPULATOR_RESOURCE_PATH)

    def manipulate(self):
        """
        Performs the offline manipulation.
        """

        assert self._src_file_path, "No source file specified!"
        assert self._dst_file_path, "No destination file specified!"

        manipulation_id = int(self._settings[TelchemyRes.DB_FIELD_MANIPULATION_ID])
        manipulation_type = self._settings[TelchemyRes.DB_FIELD_MANIPULATION_TYPE]

        if manipulation_type == TelchemyRes.MANIPULATION_TYPE_READ_TRACE:
            from telchemyManipulators.telchemyReadTraceManipulator import TelchemyReadTraceManipulator
            manipulator = TelchemyReadTraceManipulator(self, manipulation_id, self._config_path)

        elif manipulation_type == TelchemyRes.MANIPULATION_TYPE_MARKOV:
            from telchemyManipulators.telchemyMarkovManipulator import TelchemyMarkovManipulator
            manipulator = TelchemyMarkovManipulator(self, manipulation_id, self._config_path)

        else:
            raise KeyError("Unknown manipulator type: `%s`" % manipulation_type)

        manipulator.set_src_file(self._src_file_path) \
            .set_dst_file(self._dst_file_path) \
            .set_path(self._path) \
            .set_override_mode(self._is_override_mode) \
            .set_loss_trace_enabled(self._is_loss_trace_enabled) \
            .set_trace_only_state(self._is_trace_only) \
            .set_override_mode(self._is_override_mode) \
            .set_dry_mode(self._is_dry_run) \
            .set_log_settings(self._log_folder, self._log_suffix) \
            .manipulate()
