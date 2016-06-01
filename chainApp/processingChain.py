__author__ = 'Alexander Dethof'

from chainConfig import ChainConfig
from chainToolRunner import ChainToolRunner
from chainArgParser import ChainArgParser


class ProcessingChain:
    """
    Main class to execute the whole processing chain!
    """

    # name of the application this processing chain runs
    APPLICATION_NAME = 'StreamSim'

    # version name of the running application
    VERSION_NAME = 'v0.1'

    def __init__(self):
        """
        Initialization of the processing chain, i.e. the given arguments will be parsed and validated and the program's
        configuration will be loaded.
        """

        self.__config = ChainConfig()
        parser = ChainArgParser(self.__config)
        parser.reset_configuration()

        self.__tool_runner = ChainToolRunner(self.__config)

    def cleanup(self):
        """
        Cleanups the chain by invoking the clean up method on each tool which was executed during run time. Usually
        called on exiting the application.
        """

        self.__tool_runner.cleanup()

    def execute(self):
        """
        Executes the whole processing chain according to the given program arguments. I.e. the chain will execute each
        tool in the execution order until the last allowed tool (defined by the user) has been executed.
        """

        self.__tool_runner.execute()
