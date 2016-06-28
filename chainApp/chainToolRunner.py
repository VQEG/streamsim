__author__ = 'Alexander Dethof'

from copy import deepcopy
from tool.abstractTool import AbstractTool
from chainConfig import ChainConfig
from chainSetup import ChainSetup
from pvs.pvsMatrix import PvsMatrix

from tool.encodeTool import TOOL_ID_ENCODE
from tool.streamTool import TOOL_ID_STREAM
from tool.lossTool import TOOL_ID_LOSS
from tool.extractTool import TOOL_ID_EXTRACT
from tool.decodeTool import TOOL_ID_DECODE


class ChainToolRunner:

    # Tool Specification
    #
    #

    # ENCODE Tool
    SHORT_ID_ENCODE = 'enc'

    # STREAM Tool
    SHORT_ID_STREAM = 'stm'

    # LOSS Tool
    SHORT_ID_LOSS = 'los'

    # EXTRACT Tool
    SHORT_ID_EXTRACT = 'xtc'

    # DECODE Tool
    SHORT_ID_DECODE = 'dec'

    # system command ids
    TOOL_ID_RUN_ALL = 'run_all'
    TOOL_ID_CLEAN_UP = 'cleanup'
    TOOL_ID_SETUP = 'setup'

    # tools' execution order
    TOOL_EXECUTION_ORDER = (
        TOOL_ID_ENCODE,
        TOOL_ID_STREAM,
        TOOL_ID_LOSS,
        TOOL_ID_EXTRACT,
        TOOL_ID_DECODE
    )

    # action names (action which can be executed on a tool)
    ACTION_CLEANUP = 'cleanup'
    ACTION_EXECUTE = 'execute'
    ACTION_SETUP = 'setup'

    # general settings: where can the program find the config?
    PVS_CONFIG_TABLE_NAME = 'pvs'
    SRC_CONFIG_TABLE_NAME = 'src'
    HRC_CONFIG_TABLE_NAME = 'hrc'

    def __init__(self, config):
        """

        :param config:
        :return:
        """

        assert isinstance(config, ChainConfig)

        self.__config = config
        self.__setup = ChainSetup(config)

        # define short handlers
        self.__tool_id = self.__config.get_tool_id()
        self.__is_continuous_run = self.__config.is_continuous_run()

        # load pvs if required
        if self.__tool_id != self.ACTION_SETUP:
            config_path = self.__config.get_config_folder_path()
            self.__pvs_matrix = PvsMatrix(
                config_path + self.PVS_CONFIG_TABLE_NAME,
                config_path + self.SRC_CONFIG_TABLE_NAME,
                config_path + self.HRC_CONFIG_TABLE_NAME,
                self.__config.get_filters()
            )

        self.__tool = None
        self.__executed_tools = list()

    @staticmethod
    def __is_root_user():
        """
        Returns True if the current user is ROOT, False otherwise

        :return: True if the current user is ROOT, False otherwise
        """

        from os import geteuid
        return geteuid() == 0

    @staticmethod
    def __ask_for_continue_permission():
        """
        Ask the user if he want to continue with the process. If 'y' is typed in, the method is exited and the program
        can continue. If the user types in 'n', the whole program stops the execution.
        """

        ctinput = 0
        while ctinput == 0:
            ctinput = raw_input("Do you want to continue the process anyway? [y/n] ")
            if ctinput == 'y':
                return
            elif ctinput == 'n':
                exit('Chain has been aborted by user!')
            else:
                ctinput = 0

    def __check_user_privileges(self):
        """
        Checks the user privileges. It is recommended to run specific tools as root user. Others can be run as normal
        user. The setup should be run as usual user!
        """

        is_root_user = self.__is_root_user()

        if is_root_user and self.__tool_id == self.TOOL_ID_SETUP:
            print "It is recommended to perform the \x1b[36m\033[1msetup\033[0m as \x1b[36m\033[1mnormal user\033[0m."
            self.__ask_for_continue_permission()

        elif not is_root_user and self.__tool_id != self.TOOL_ID_SETUP:
            print "It is recommended to run \x1b[36m\033[1many tool\033[0m (without the setup) " \
                  "as \x1b[36m\033[1mroot user\033[0m."
            self.__ask_for_continue_permission()

    def __log_tool_info(self, tool_name, action_name):
        """
        Function which can be used to dump a message into the console to notify about the current action which will
        be executed on a given tool.
        :param tool_name: The name of the tool on which an action is performed
        :param action_name: The name of the action to execute
        """

        assert isinstance(tool_name, basestring)
        assert isinstance(action_name, basestring)

        self.__log_info_box('%s processing tool: `%s`' % (action_name.capitalize(), tool_name))

    @staticmethod
    def __log_info_box(text):
        """
        Logs a big box in the console, with some text placed in.
        :param text: the text to display
        """

        decorated_text = "%s" % text
        box_line = '#' * (len(decorated_text) + 6)  # + 6 = 2 * 2 spaces + 2 * #
        print '\n%s\n#  \033[1m\033[92m%s\033[0m  #\n%s\n' % (box_line, decorated_text, box_line)

    def __get_tool_specific_config(self, tool_id):
        """

        :param tool_id:
        :return:
        """

        config = deepcopy(self.__config)
        assert isinstance(config, ChainConfig)

        tool_options = config.get_tool_options()

        if tool_id in tool_options:
            tool_options = {tool_id: tool_options[tool_id]}
        else:
            tool_options = dict()

        # override config tool options only with the relevant ones, the others are not interesting!
        config.set_tool_options(tool_options)

        # set the id of the current tool to execute
        config.set_tool_id(tool_id)

        return config

    def __init_encode_tool(self, config):
        """
        Loads into the chain's tool attribute a new encoding tool with the chain's pvs configuration
        """

        from tool.encodeTool import EncodeTool
        self.__tool = EncodeTool(self.__pvs_matrix, config)

    def __init_stream_tool(self, config):
        """
        Loads into the chain's tool attribute a new streaming tool with the chain's pvs configuration
        """

        from tool.streamTool import StreamTool
        self.__tool = StreamTool(self.__pvs_matrix, config)

    def __init_loss_tool(self, config):
        """
        Loads into the chain's tool attribute a new loss-insertion tool with the chain's pvs configuration
        """

        from tool.lossTool import LossTool
        self.__tool = LossTool(self.__pvs_matrix, config)

    def __init_decode_tool(self, config):
        """
        Loads into the chain's tool attribute a new decoding tool with the chain's pvs configuration
        """

        from tool.decodeTool import DecodeTool
        self.__tool = DecodeTool(self.__pvs_matrix, config)

    def __init_extract_tool(self, config):
        """
        Loads into the chain's tool attribute a new payload-extraction tool with the chain's pvs configuration
        """

        from tool.extractTool import ExtractTool
        self.__tool = ExtractTool(self.__pvs_matrix, config)

    def __init_tool(self, tool_id):
        """
        Initializes a tool specified by its given id. If no tool was found according to the given id,
        a key error is thrown. If the tool could be loaded successfully it is placed into the chain's tool attribute.

        :param tool_id: the id of the tool to initialize
        :raise KeyError: if no tool was found for the given id
        """

        self.__setup.check_tool_setup(tool_id)
        config = self.__get_tool_specific_config(tool_id)

        if tool_id == TOOL_ID_ENCODE:
            self.__init_encode_tool(config)

        elif tool_id == TOOL_ID_STREAM:
            self.__init_stream_tool(config)

        elif tool_id == TOOL_ID_LOSS:
            self.__init_loss_tool(config)

        elif tool_id == TOOL_ID_DECODE:
            self.__init_decode_tool(config)

        elif tool_id == TOOL_ID_EXTRACT:
            self.__init_extract_tool(config)

        else:
            raise KeyError('No tool could be loaded for id `%s`' % tool_id)

        # connect tool with log folder, if enabled
        if self.__config.is_log_mode():
            tool_log_folder = self.__config.get_log_folder_path() + tool_id

            from os.path import exists
            if not exists(tool_log_folder):
                from os import mkdir
                mkdir(tool_log_folder)

            self.__tool.set_log_folder(tool_log_folder)

    def __run_tool_action(self, tool_id, action_name):
        """
        Initializes a tool in the chain given by its id and invokes a specified action on it.

        :param tool_id: the id of the tool to initialize and to invoke the action on
        :param action_name: the name of the action to invoke
        :raise KeyError: if the tool could not be initialized or no tool method was specified according to the given
         action
        """

        self.__log_tool_info(tool_id, action_name)
        self.__init_tool(tool_id)
        assert isinstance(self.__tool, AbstractTool)

        if action_name == self.ACTION_EXECUTE:
            self.__executed_tools.append(self.__tool)
            self.__tool.execute()

        elif action_name == self.ACTION_CLEANUP:
            self.__tool.cleanup()

        else:
            raise KeyError('Unknown action name given: `%s`' % action_name)

    def cleanup(self):
        """

        :return:
        """

        if self.__executed_tools:

            print "!! Processing clean up before exit ...\n"

            for tool in self.__executed_tools:
                tool.cleanup()

            print "... Clean up finished !!\n"

    def execute(self):
        """

        :return:
        """

        # check if there is a conflict in the execution modes given and raise a syntax error if so
        if self.__config.is_single_run() and self.__is_continuous_run and self.__tool_id in self.TOOL_EXECUTION_ORDER:
            raise SyntaxError(
                "You run the application in \x1b[36m\033[1msingle and continuous mode\033[0m"
                " - Unfortunately this is not possible. Please correct your call!"
            )

        if self.__config.is_override_mode():
            print "You set the chain to be run in \x1b[36m\033[1mOverride mode\033[0m - that will override all previous " \
                  "changes done with the chain."
            self.__ask_for_continue_permission()

        if self.__config.is_dry_run():
            self.__log_info_box('ATTENTION: The following commands will be run dry - no changes will be done !!')

        self.__check_user_privileges()

        is_execution_allowed = self.__tool_id == self.TOOL_ID_RUN_ALL \
                               or self.__tool_id == self.TOOL_ID_CLEAN_UP \
                               or self.__tool_id == self.TOOL_ID_SETUP \
                               or (self.__is_continuous_run and self.__tool_id == TOOL_ID_ENCODE) \
                               or not self.__is_continuous_run

        if self.__tool_id == self.ACTION_SETUP:
            self.__setup.setup()
            return

        if self.__tool_id != self.ACTION_SETUP:
            from os.path import isdir

            log_folder_path = self.__config.get_log_folder_path()
            assert isdir(log_folder_path), \
                "The log folder `%s` does not exist. Please create it manually or re-run the setup!" % log_folder_path

            config_folder_path = self.__config.get_config_folder_path()
            assert isdir(log_folder_path), \
                "The config folder `%s` does not exist. Please create it manually or re-run the setup!" % config_folder_path

        for tool_id in self.TOOL_EXECUTION_ORDER:

            if not is_execution_allowed:
                if tool_id == self.__tool_id and self.__is_continuous_run:
                    is_execution_allowed = True

            if is_execution_allowed:
                if self.__tool_id == self.TOOL_ID_CLEAN_UP:
                    self.__run_tool_action(tool_id, self.ACTION_CLEANUP)

                elif not self.__config.is_single_run() or tool_id == self.__tool_id or self.__tool_id == self.TOOL_ID_RUN_ALL:
                    self.__run_tool_action(tool_id, self.ACTION_EXECUTE)

            # This line will hinder the script to execute further tools
            if tool_id == self.__tool_id and not self.__is_continuous_run:
                break
