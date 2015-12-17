__author__ = 'Alexander Dethof'

#
# List of allowed codecs
#
CODEC_ID_XLIB_264 = 'x264'  # x264 codec
CODEC_ID_XLIB_265 = 'x265'  # x265 codec


def __get_codec_unchecked(codec_id, codec_settings_id, config_folder_path):
    """
    Returns a codec class representing the codec settings of the appropriate configuration table. If the appropriate
    codec could not be found an error is thrown.

    :param codec_id: the id of the codec to look for
    :type codec_id: basestring

    :param codec_settings_id: the id of the configuring data set in the codec's configuration table
    :type codec_settings_id: int

    :param config_folder_path: the path to the folder where the pvs configuration is put
    :type config_folder_path: basestring

    :return: a codec class representing the codec settings of the appropriate configuration table. If the appropriate
    codec could not be found an error is thrown.
    """

    assert isinstance(codec_id, basestring)
    assert isinstance(codec_settings_id, int)
    assert isinstance(config_folder_path, basestring)

    # map for x264 codec
    if codec_id == CODEC_ID_XLIB_264:
        from x264Codec import X264Codec
        return X264Codec(codec_settings_id, config_folder_path)

    # map for x265 codec
    if codec_id == CODEC_ID_XLIB_265:
        from x265Codec import X265Codec
        return X265Codec(codec_settings_id, config_folder_path)

    #
    # ... space for further codec id mappings ...
    #
    # [SCHEME: if codec_id == '<CODEC_ID>':]
    # ....
    #
    #

    raise KeyError("The given codec id `%s` could not be mapped to an implemented codec class!" % codec_id)


def get_codec(codec_id, codec_settings_id, config_folder_path):
    """
    Returns a codec class representation given for a specific codec id and validates it if it is a correct codec
    extending the class `AbstractCodec`

    :param codec_id: the id to look the codec for
    :type codec_id: basestring

    :param codec_settings_id: the id of the settings defined in the codec's configuration file
    :type codec_settings_id: int

    :param config_folder_path: the path to the folder where the pvs configuration is put
    :type config_folder_path: basestring

    :return: a codec class representation given for a specific codec id which extends the class `AbstractCodec`
    :rtype: codec.abstractCodec.AbstractCodec
    """

    assert isinstance(codec_id, basestring)
    assert isinstance(codec_settings_id, int)

    codec = __get_codec_unchecked(codec_id, codec_settings_id, config_folder_path)

    from abstractCodec import AbstractCodec
    assert isinstance(codec, AbstractCodec)

    return codec


def get_meta_descriptions():
    """
    Returns the meta descriptions of all available codecs
    :return: meta descriptions of all available codecs
    """

    from x264Codec import X264Codec
    from x265Codec import X265Codec

    return (
        X264Codec.get_meta_description(),
        X265Codec.get_meta_description()
    )
