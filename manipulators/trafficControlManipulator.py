__author__ = 'Alexander Dethof'

from multiprocessing import Process

from abstractManipulator import AbstractManipulator
from cmd.command import Command
from tool.streamTool import STREAM_NETWORK_INTERFACE, STREAM_PROTOCOL_UDP, STREAM_PORT
from manipulators.resources.trafficControlManipulatorResource import TrafficControlManipulatorResource as TCRes

# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR


class TrafficControlManipulator(AbstractManipulator):
    """
    Class to represent an online manipulation by configuring the traffic settings and replaying the pcap file in this
    modified network.
    """

    # path of the manipulator resource table
    MANIPULATOR_RESOURCE_PATH = 'hrc' + PATH_SEPARATOR + 'packet_loss' + PATH_SEPARATOR + 'tc'

    def _get_resource_handler(self):
        """
        Returns the resource handler for the online manipulation.

        :return: The resource handler for the online manipulation
        """

        return TCRes(self._config_path + self.MANIPULATOR_RESOURCE_PATH)

    @staticmethod
    def __get_new_tc_add_command():
        """
        Generates and returns a command for the TC tool, which adds a qdisc-operation.

        :return: A TC command which adds a qdisc-operation
        :rtype: Command
        """

        """
        tc: http://lartc.org/manpages/tc.txt

        qdisc <OPERATOR=add|change|del|replace|link>: defines the operation to be done on the traffic control
        dev <DEVICE>: sets the device to set the traffic control for
        <NODE=root|parent>: node of the device to operate in
        """

        tc_command = Command('tc')
        tc_command.set_as_argument('QDISC-OPERATION', 'qdisc add') \
                  .set_as_argument('DEVICE', 'dev %s root' % STREAM_NETWORK_INTERFACE)

        return tc_command

    def __manipulate_time_behaviour(self):
        """
        Generates and executes a TC command, which will manipulate the network's time behaviour (i.e. delay, jitter).
        """

        distribution = self._settings[TCRes.DB_JITTER_DISTRIBUTION_FIELD_NAME]

        delay = float(self._settings[TCRes.DB_DELAY_FIELD_NAME]) # in ms
        if distribution == TCRes.DB_JITTER_DISTRIBUTION_VALUE_NONE and delay == TCRes.DB_DELAY_VALUE_NONE:
            return

        """
        netem: http://www.linuxfoundation.org/collaborate/workgroups/networking/netem

        delay <DELAY_IN_MS>ms [<JITTER_IN_MS>ms [<DISTRIBUTION>%|distribution <DISTRIBUTION_TYPE>]]:
          sets a delay of <DELAY_IN_MS> ms and optionally a jitter of <JITTER_IN_MS>ms can be defined. Further more
          a distribution can be set for the jitter.
        """

        tc_command = self.__get_new_tc_add_command()
        tc_command.set_as_argument('NETEM', 'netem') \
                  .set_as_argument('DELAY', 'delay %.2fms %.2fms distribution %s' % (
                      delay,
                      float(self._settings[TCRes.DB_JITTER_FIELD_NAME]),
                      distribution
                  )
        )

        self._cmd(tc_command)

    def __apply_random_model_on_tc(self, tc_command, loss_mode_id):
        """
        Applies the random model on a given TC command.

        :param tc_command: The command to apply the model to.
        :type tc_command: Command

        :param loss_mode_id: The id linked to the settings specifying the model.
        :type loss_mode_id: int
        """

        assert isinstance(tc_command, Command)
        assert isinstance(loss_mode_id, int)

        from manipulators.resources.trafficControlManipulatorResource \
            import TrafficControlManipulatorRandomModeResource \
            as TCLossRes

        tc_loss_res = TCLossRes(self.MANIPULATOR_RESOURCE_PATH + PATH_SEPARATOR + 'random')
        loss_mode_settings = tc_loss_res.get_row_with_id(loss_mode_id)

        tc_command.set_as_argument('LOSS_MODE', 'random') \
                  .set_as_argument('LOSS_RATE', '%.2f%%' % (
                      float(loss_mode_settings[TCLossRes.DB_LOSS_RATE_FIELD_NAME])
                  ))

    def __apply_state_model_on_tc(self, tc_command, loss_mode_id):
        """
        Applies a state model on a given TC command.

        :param tc_command: The command to apply the model to.
        :type tc_command: Command

        :param loss_mode_id: The id linked to the settings specifying the model.
        :type loss_mode_id: int
        """

        assert isinstance(tc_command, Command)
        assert isinstance(loss_mode_id, int)

        from manipulators.resources.trafficControlManipulatorResource \
            import TrafficControlManipulatorStateModeResource \
            as TCLossRes

        tc_loss_res = TCLossRes(self.MANIPULATOR_RESOURCE_PATH + PATH_SEPARATOR + 'state')
        loss_mode_settings = tc_loss_res.get_row_with_id(loss_mode_id)

        tc_command.set_as_argument('LOSS_MODE', 'state') \
                  .set_as_argument('P13', '%.2f%%' % float(loss_mode_settings[TCLossRes.DB_P13_FIELD_NAME]))

        p_args = ('P31', 'P32', 'P23', 'P14')
        p_vals = {
            'P31': TCLossRes.DB_P31_FIELD_NAME,
            'P32': TCLossRes.DB_P32_FIELD_NAME,
            'P23': TCLossRes.DB_P23_FIELD_NAME,
            'P14': TCLossRes.DB_P14_FIELD_NAME
        }

        for p_arg in p_args:
            p_val = p_vals[p_arg]
            if p_val in loss_mode_settings:
                tc_command.set_as_argument(p_arg, '%.2f%%' % float(loss_mode_settings[p_val]))
            else:
                break

    def __apply_ge_model_on_tc(self, tc_command, loss_mode_id):
        """
        Applies a Gilbert-Elliot model on a given TC command.

        :param tc_command: The command to apply the model to.
        :type tc_command: Command

        :param loss_mode_id: the id which is linked to the appropriate Gilbert-Elliot manipulation settings
        :type loss_mode_id: int
        """

        assert isinstance(tc_command, Command)
        assert isinstance(loss_mode_id, int)

        from manipulators.resources.trafficControlManipulatorResource \
            import TrafficControlManipulatorGeModelResource \
            as TCLossRes

        tc_loss_res = TCLossRes(self.MANIPULATOR_RESOURCE_PATH + PATH_SEPARATOR + 'gemodel')
        loss_mode_settings = tc_loss_res.get_row_with_id(loss_mode_id)

        tc_command.set_as_argument('LOSS_MODE', 'gemodel') \
                  .set_as_argument('BADPRB', '%.2f%%' % float(loss_mode_settings[TCLossRes.DB_BAD_PROB_FIELD_NAME]))

        p_args = ('GOODPRB', 'GOODLOSSPROB', 'BADLOSSPROB')
        p_vals = {
            'GOODPRB': TCLossRes.DB_GOOD_PROB_FIELD_NAME,
            'GOODLOSSPROB': TCLossRes.DB_GOOD_LOSS_PROB_FIELD_NAME,
            'BADLOSSPROB': TCLossRes.DB_BAD_LOSS_PROB_FIELD_NAME
        }

        for p_arg in p_args:
            p_val = p_vals[p_arg]
            if p_val in loss_mode_settings:
                tc_command.set_as_argument(p_arg, '%.2f%%' % float(loss_mode_settings[p_val]))
            else:
                break

    def __manipulate_space_behaviour(self):
        """
        Sets up a TC command which will modify the loss behaviour, in terms of loss rate and additional variations and
        executes it.
        """

        """
        netem: http://www.linuxfoundation.org/collaborate/workgroups/networking/netem

        loss random <LOSS_RATE_%>% [<VARIATION_%>]: sets a random loss rate distribution in % with an
            optional variation factor
        """

        tc_command = self.__get_new_tc_add_command()
        tc_command.set_as_argument('NETEM', 'netem') \
                  .set_as_argument('LOSS', 'loss')

        loss_mode = self._settings[TCRes.DB_LOSS_MODE_FIELD_NAME]
        loss_mode_id = int(self._settings[TCRes.DB_LOSS_MODE_ID_FIELD_NAME])

        if loss_mode == TCRes.DB_LOSS_MODE_RANDOM_VALUE:
            self.__apply_random_model_on_tc(tc_command, loss_mode_id)

        elif loss_mode == TCRes.DB_LOSS_MODE_STATE_VALUE:
            self.__apply_state_model_on_tc(tc_command, loss_mode_id)

        elif loss_mode == TCRes.DB_LOSS_MODE_GE_VALUE:
            self.__apply_ge_model_on_tc(tc_command, loss_mode_id)

        self._cmd(tc_command)

    def __handle_tcpdump_on_destination(self):
        """
        Starts a "tcpdump" process, which captures packets transmitted over the network and collects them in a
        pre-specified destination file.

        :return: The tcpdump process which is used to dump the transmitted packets into the destination file
        :rtype: Process
        """

        """
        tcpdump: http://www.tcpdump.org/tcpdump_man.html

        -i <INPUT>: specifies input resource
        -w <OUTPUT>: specifies output resource to write pcap content

        additional filter used here: '<PROTOCOL> port <PORT>'
        --> Capture only all packets which are delivered via the <PROTOCOL> protocol over port <PORT>
        """

        tcpdump_command = Command('tcpdump')
        tcpdump_command.set_as_subprocess() \
                       .set_as_posix_option('i', STREAM_NETWORK_INTERFACE) \
                       .set_as_posix_option('w', self._dst_file_path) \
                       .set_as_argument('PROTOCOL', STREAM_PROTOCOL_UDP) \
                       .set_as_argument('PORT', 'port %d' % STREAM_PORT)

        # set loggings
        if self._log_folder and self._log_suffix:
            tcpdump_log_file_path = self._get_log_file_path('tcpdump')
            tcpdump_command.set_as_log_file(tcpdump_log_file_path) \
                           .set_std_err_redirect_to_file()

        process = self._cmd(tcpdump_command)

        # wait a short time wherein the process is able to initialize itself
        if not self._is_dry_run:
            from time import sleep
            sleep(1)

        return process

    def __replay_stream(self):
        """
        Replays the pre-specified packet source stream.
        """

        """
        tcpreplay: http://tcpreplay.synfin.net/wiki/tcpreplay

        -i <NETWORK_INTERFACE>: replay packets to the interface <NETWORK_INTERFACE>

        <INPUT>: input resource to replay the packets from
        """

        tcpreplay_command = Command('tcpreplay')
        tcpreplay_command.set_as_posix_option('i', STREAM_NETWORK_INTERFACE) \
                         .set_as_argument('INPUT', self._src_file_path)

        if self._log_folder:
            from os import devnull
            tcpreplay_log_file_path = self._get_log_file_path('tcpreplay')
            tcpreplay_command.set_std_err_redirect_to_std_out() \
                             .tee(tcpreplay_log_file_path + ' > ' + devnull) \

        self._cmd(tcpreplay_command)

    def __redump_stream(self):
        """
        Replays the packet stream and dumps it to the pre-specified destination file.
        """

        tcpdump_process = self.__handle_tcpdump_on_destination()

        self.__replay_stream()

        if isinstance(tcpdump_process, Process):
            self._terminate_process_with_children(tcpdump_process)


    def manipulate(self):
        """
        Performs the online manipulation.
        """

        assert self._src_file_path, "No source file specified!"
        assert self._dst_file_path, "No destination file specified!"

        if self._is_trace_only:
            # the loss tool will perform the tracing
            return

        self.__manipulate_time_behaviour()
        self.__manipulate_space_behaviour()

        self.__redump_stream()

        self.cleanup()

    def cleanup(self):
        """
        Cleans up on exiting the application, i.e. the manipulation settings are reverted to normal settings.
        """

        """
        tc: http://lartc.org/manpages/tc.txt

        qdisc <OPERATOR=add|change|del|replace|link>: defines the operation to be done on the traffic control
        dev <DEVICE>: sets the device to set the traffic control for
        <NODE=root|parent>: node of the device to operate in
        """

        # delete tc settings -> reset to default
        tc_cleanup_command = Command('tc')
        tc_cleanup_command.set_as_argument('QDISC-OPERATION', 'qdisc del') \
                          .set_as_argument('DEVICE', 'dev %s root' % STREAM_NETWORK_INTERFACE)

        self._cmd(tc_cleanup_command)