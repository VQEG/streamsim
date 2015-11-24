__author__ = 'Alexander Dethof'

#
# List of allowed coding ids
#

# id for the ffmpeg coder
FFMPEG_CODER_ID = 'ffmpeg'

# valid coder id list
VALID_CODER_IDS = (
    FFMPEG_CODER_ID
)

#
# ... space for more coding ids ...
#


def __get_coder(coder_id, config_folder_path):
    """
    This method loads a coder for the given coding id. The returned coder of this method is not checked to be a valid
     one. Hence this method should be only used internally.

    :param coder_id: the id to return a coder for
    :type coder_id: basestring

    :param config_folder_path: the path where the pvs configuration is put
    :type config_folder_path: basestring

    :return: the appropriate coder
    :rtype: AbstractCoder

    :raises KeyError: if the requested coder was not found
    """

    assert isinstance(coder_id, basestring)
    assert isinstance(config_folder_path, basestring)

    # map for FFMPEG coder
    if coder_id == FFMPEG_CODER_ID:
        from ffmpegCoder import FfmpegCoder
        return FfmpegCoder(config_folder_path)

    #
    # ... space for further coder id mappings ...
    #
    # [SCHEME: if coding_id == '<CODING_ID>':]
    # ....
    #
    #

    raise KeyError('No coder found for id `%s`' % coder_id)


def get_validated_coder(coding_id, config_folder_path):
    """
    This method can be used to load a coder for a given coding id. If the coder id is unknown a key error will be
    thrown, which indicates that there was no coder found.

    :param coding_id: the id to return a coder for
    :type coding_id: basestring

    :param config_folder_path: the path where the pvs configuration is put
    :type config_folder_path: basestring

    :return: the appropriate coder
    :rtype: AbstractCoder
    """

    assert isinstance(coding_id, basestring)
    assert isinstance(config_folder_path, basestring)

    coder = __get_coder(coding_id, config_folder_path)

    from abstractCoder import AbstractCoder
    assert isinstance(coder, AbstractCoder), "The coder `%s` does not extend the class `%s`." % (
        coder.__class__.__name__, AbstractCoder.__name__
    )

    return coder