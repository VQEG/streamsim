__author__ = 'Alexander Dethof'

from tool.encodeTool import ENCODER_SOURCE_DIR, ENCODER_DESTINATION_DIR, TOOL_ID_ENCODE
from tool.streamTool import STREAM_DESTINATION_DIR, TOOL_ID_STREAM
from tool.lossTool import LOSS_DESTINATION_DIR, TOOL_ID_LOSS
from tool.extractTool import EXTRACT_DESTINATION_DIR, TOOL_ID_EXTRACT
from tool.decodeTool import DECODER_DESTINATION_DIR, TOOL_ID_DECODE

from os.path import isdir
from chainConfig import ChainConfig


class ChainSetup:
    """

    """

    REQUIRED_FOLDERS = {
        TOOL_ID_ENCODE: [ENCODER_SOURCE_DIR, ENCODER_DESTINATION_DIR],
        TOOL_ID_STREAM: [STREAM_DESTINATION_DIR],
        TOOL_ID_LOSS: [LOSS_DESTINATION_DIR],  # TODO integrate traces dir
        TOOL_ID_EXTRACT: [EXTRACT_DESTINATION_DIR],
        TOOL_ID_DECODE: [DECODER_DESTINATION_DIR]
    }

    def __init__(self, config):
        """

        :return:
        """

        assert isinstance(config, ChainConfig)
        self.__config = config

    def __setup_dir(self, dir_path):
        """
        Setups a folder with the given dir name and if it already exists, asks the user what to do.

        :param dir_path: the path to create
        :type dir_path: basestring
        """

        # TODO split code in sub functions

        assert isinstance(dir_path, basestring)

        if self.__config.is_dry_run():
            return

        from os.path import isdir

        if isdir(dir_path):
            if self.__config.is_override_mode():
                from shutil import rmtree

                rmtree(dir_path)
            else:
                print "The folder `%s` already exists. Continuing the setup will remove all data inside!" % dir_path

                ctsetup = 0
                while ctsetup == 0:
                    ctsetup = raw_input(
                        "How do you want to go on? (s = skip, c = continue anyway, b = continue with backup, q = quit) "
                    )

                    if ctsetup == 's':
                        return
                    elif ctsetup == 'b':
                        # TODO force sudo in this step!

                        from shutil import copytree, rmtree
                        # noinspection PyPep8Naming
                        from os import mkdir, sep as PATH_SEPARATOR

                        backup_dir = self.__config.get_path() + 'backup'
                        if not isdir(backup_dir):
                            mkdir(backup_dir)

                        from time import time
                        path_elements = dir_path.split(PATH_SEPARATOR)
                        path_elements = [element for element in path_elements if element]
                        dir_name = path_elements[len(path_elements) - 1]

                        backup_path = backup_dir + PATH_SEPARATOR + dir_name + '_' + str(time())
                        copytree(dir_path, backup_path)
                        print 'Did backup of `%s` in `%s`' % (dir_path, backup_path)

                        rmtree(dir_path)

                    elif ctsetup == 'q':
                        exit('Chain was aborted by user!')
                    elif ctsetup == 'c':
                        from shutil import rmtree

                        rmtree(dir_path)
                    else:
                        ctsetup = 0

        from os import mkdir
        print "MKDIR: %s" % dir_path
        mkdir(dir_path)

    def __setup_tool(self, tool_id):
        """

        :param tool_id:
        :return:
        """

        folder_names = self.REQUIRED_FOLDERS[tool_id]
        for folder_name in folder_names:
            self.__setup_dir(self.__config.get_path() + folder_name)

    def __setup_config(self):
        """

        :return:
        """

        from metaConfig.metaTree import MetaTree
        tree = MetaTree(self.__config.get_config_folder_path())

        # build tree from root
        from pvs.pvsMatrix import PvsMatrix
        root_node = PvsMatrix.get_meta_description()
        tree.set_root_node(root_node)

        from pvs.srcTable import SrcTable
        root_node.add_sibling(SrcTable.get_meta_description())

        from pvs.hrcTable import HrcTable
        hrc_node = HrcTable.get_meta_description()
        root_node.add_sibling(hrc_node)

        tree.generate_files()

        from coder.codec import codecList
        codec_meta_descriptions = codecList.get_meta_descriptions()

        from os import mkdir
        from os.path import sep as PATH_SEPARATOR
        codec_config_file_path = self.__config.get_config_folder_path() + 'codec' + PATH_SEPARATOR # FIXME hard-code
        mkdir(codec_config_file_path)

        from metaConfig.metaTable import MetaTable
        for codec_meta_description in codec_meta_descriptions:
            assert isinstance(codec_meta_description, MetaTable)
            codec_meta_description.generate_file(codec_config_file_path)

    def setup(self):
        """

        :return:
        """

        # setup system folders
        self.__setup_dir(self.__config.get_config_folder_path())
        self.__setup_dir(self.__config.get_log_folder_path())

        # .. and the config files
        self.__setup_config()

        # setup tool folders
        for tool_id in self.REQUIRED_FOLDERS:
            self.__setup_tool(tool_id)

    def check_tool_setup(self, tool_id):
        """
        Checks if the folders required for a given tool exist.

        :param tool_id: the id of the tool to check the requirements for
        :type tool_id: basestring
        """

        folders = self.REQUIRED_FOLDERS[tool_id]

        for folder in folders:
            assert isdir(self.__config.get_path() + folder), \
                "The tool `%s` requires the folder `%s`, but it does not exist! " \
                "Please run setup first and rerun than the actual command! See `help` for further information!" % (
                    tool_id, folder
                )