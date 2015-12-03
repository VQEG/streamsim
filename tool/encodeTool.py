__author__ = 'Alexander Dethof'

# the source dir containing the raw videos to encode
ENCODER_SOURCE_DIR = 'srcVid'

# the destination dir containing in which the encoded hevc videos should be packed in
ENCODER_DESTINATION_DIR = 'outputHevc'

# tool id
TOOL_ID_ENCODE = 'encode_videos'

from abstractTool import AbstractTool
# noinspection PyPep8Naming
from os import sep as PATH_SEPARATOR, remove
from os.path import exists
from pvs.hrc.encodingTable import EncodingTable
from coder.coderList import get_validated_coder


class EncodeTool(AbstractTool):
    """
    This tool is used to encode all given raw videos in the encoder's source dir to the appropriate hevc videos in the
    encoder's output dir.
    """

    def __init__(self, pvs_matrix, config):
        """
        Initialization of the tool. Loads the given pvs matrix into the tool and connects it to the encoding table,
        which contains the settings to use in encoding processes.

        :param pvs_matrix: the pvs matrix to load into the tool
        :type pvs_matrix: pvs.pvsMatrix.PvsMatrix

        :param config: the config used for the tool's execution
        :type config: chain_app.metaConfig.ChainConfig
        """

        super(self.__class__, self).__init__(pvs_matrix, config)
        self.__encoding_table = pvs_matrix.get_hrc_table().get_encoding_table()
        self.__src_enc_references = dict()

    def __encode_source_by_hrc(self, src_id, src_name, hrc_set):
        """
        Encodes a given video source according to a specific HRC definition.

        :param src_id: the id of the source to encode
        :type src_id: int

        :param src_name: the name of the source to encode
        :type src_name: basestring

        :param hrc_set: the set defining the HRC
        :type hrc_set: dict
        """

        # check if args are valid
        assert isinstance(src_id, int)
        assert isinstance(hrc_set, dict)

        # request hrc id
        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
        hrc_id = int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID])

        # get id of encode settings
        assert EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID in hrc_set
        encoding_id = int(hrc_set[EncodingTable.DB_TABLE_FIELD_NAME_ENCODING_ID])

        assert self._hrc_table.DB_TABLE_FIELD_NAME_CODER_ID in hrc_set
        coding_id = hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_CODER_ID]

        # setup coder
        coder = get_validated_coder(coding_id, self._config.get_config_folder_path())
        codec = self._get_codec_by_hrc_set(hrc_set)

        destination_path = self._path \
                           + ENCODER_DESTINATION_DIR \
                           + PATH_SEPARATOR \
                           + self._get_output_file_name(
                                src_id,
                                hrc_set,
                                'mov'  # codec.get_raw_file_extension() # TODO
                            )

        if self._IS_INFO_MODE:
            print 'HRC: %d (ENC: %d)' % (hrc_id, encoding_id)

        # encode video with the coder given in the HRC definition

        # check if the destination path already exists -> check override mode to skip or to override
        assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
        if exists(destination_path):
            if self._is_override_mode:
                if not self._is_dry_run:
                    remove(destination_path)
                print "# \033[95m\033[1mREMOVE src %d : hrc %d\033[0m" \
                      % (src_id, int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID]))
            else:
                assert self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID in hrc_set
                print "# \033[95m\033[1mSKIP src %d : hrc %d\033[0m" \
                      % (src_id, int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID]))
                return  # !!

        # check if the encoding has been done onetime, if so just copy the file from previous HRC
        if encoding_id in self.__src_enc_references[src_id]:
            ref_hrc_id = self.__src_enc_references[src_id][encoding_id]
            ref_hrc_set = self._hrc_table.get_row_with_id(ref_hrc_id)
            ref_file_path = self._path \
                            + ENCODER_DESTINATION_DIR \
                            + PATH_SEPARATOR \
                            + self._get_output_file_name(
                                src_id,
                                ref_hrc_set,
                                codec.get_raw_file_extension()
                            )

            print "# \033[93m\033[1mDUPLICATE src %d : hrc %d (Reference is HRC %d)\033[0m"\
                  % (src_id, int(hrc_set[self._hrc_table.DB_TABLE_FIELD_NAME_HRC_ID]), ref_hrc_id)

            if not self._is_dry_run:
                from shutil import copyfile
                copyfile(ref_file_path, destination_path)
            return  # !!

        coder.set_src_path(self._path + ENCODER_SOURCE_DIR + PATH_SEPARATOR + src_name) \
             .set_destination_path(destination_path)

        # get encoding set
        encoding_set = self.__encoding_table.get_row_with_id(encoding_id)

        if self._log_folder:
            log_file_path = self._log_folder + PATH_SEPARATOR + self._get_output_file_name(src_id, hrc_set, 'log')
            coder.set_log_file(log_file_path)

        # execute coder
        coder.set_dry_mode(self._is_dry_run) \
             .encode(encoding_set)

        # register encoding id with hrc id in references
        self.__src_enc_references[src_id][encoding_id] = hrc_id

    def __encode_source_by_hrcs(self, src_id, src_name, hrc_sets):
        """
        Encodes a given video source according to the given HRC definitions.

        :param src_id: the id of the source to encode
        :type src_id: int

        :param src_name: the name of the source to encode
        :type src_name: basestring

        :param hrc_sets: the HRC configurations to encode the video with
        :type hrc_sets: dict[]
        """

        assert isinstance(src_id, int)
        assert isinstance(src_name, basestring)
        assert isinstance(hrc_sets, list)

        # if not done yet, create an entry in the source's encoding reference list
        if src_id not in self.__src_enc_references:
            self.__src_enc_references[src_id] = dict() # dict(encoding_id => hrc_id)
            #  -> first hrc_id which used this encoding id

        # raise warning if a source has no HRC with which it can be decoded
        if not hrc_sets:
            raise Warning('No HRC given for source `%s`' % src_name)

        # loop through the sets and encode the video with each HRC definition
        for hrc_set in hrc_sets:
            self.__encode_source_by_hrc(src_id, src_name, hrc_set)

    def __encode_source(self, src_id, src_name):
        """
        This method will find the appropriate HRC definitions for a given source and executes an encoding process for
        each HRC definition on the source.

        :param src_id: the id of the source
        :type src_id: int

        :param src_name: the name of the source
        :type src_name: basestring
        """

        assert isinstance(src_id, int)
        assert isinstance(src_name, basestring)

        # load encoding configuration of the given source
        hrc_sets = self._pvs_matrix.get_hrc_sets_of_src_id(src_id)

        # encode video with the settings
        self.__encode_source_by_hrcs(src_id, src_name, hrc_sets)

    def execute(self):
        """
        Executes the tool and encodes all videos which are set in the PVS matrix's SRC table and stored in the tool's
        source dir to hevc videos.
        """

        super(self.__class__, self).execute()

        for source in self._src_sets:

            assert isinstance(source, dict)
            assert self._src_table.DB_TABLE_FIELD_NAME_SRC_ID in source
            assert self._src_table.DB_TABLE_FIELD_NAME_SRC_NAME in source

            # get source fields
            src_id = int(source[self._src_table.DB_TABLE_FIELD_NAME_SRC_ID])
            src_name = source[self._src_table.DB_TABLE_FIELD_NAME_SRC_NAME]

            if self._IS_INFO_MODE:
                print '--> ENCODE source -- id: %d | name: %s' % (src_id, src_name)

            try:
                # encode video
                self.__encode_source(src_id, src_name)
            except (KeyError, Warning) as e:
                # Key errors and Warnings are usually internal errors which can be ignored during the encoding process.
                # They will only lead to the circumstance that not all videos could be converted with the given
                # settings. The tool should be able to tolerate this, but will still log the problems.
                self._append_exception(e)

        # show summary of all errors and warnings collected
        self._show_we_summary()