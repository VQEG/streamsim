__author__ = 'Alexander Dethof'

from abc import ABCMeta, abstractmethod
from bitstreamparse.rtpParser import RtpParser


class RawVideo(RtpParser):

    __metaclass__ = ABCMeta

    #
    # rtp specific constants
    #

    DYNAMIC_PAYLOAD_TYPE_ID_MIN = 96
    DYNAMIC_PAYLOAD_TYPE_ID_MAX = 127

    #
    # nal unit specific constants
    #

    NAL_UNIT_FIELD_FORBIDDEN = 'forbidden'
    NAL_UNIT_FIELD_LAYER_ID = 'layer_id'
    NAL_UNIT_FIELD_TYPE = 'type'
    NAL_UNIT_FIELD_TID = 'tid'

    def _is_valid_payload_type(self, payload_type):
        assert isinstance(payload_type, int), 'Invalid payload type given!'

        return self.DYNAMIC_PAYLOAD_TYPE_ID_MIN <= payload_type <= self.DYNAMIC_PAYLOAD_TYPE_ID_MAX

    @abstractmethod
    def _parse_payload_header(self, payload_header):
        pass

    @abstractmethod
    def _parse_nal_unit(self, nal_unit):
        pass

    @abstractmethod
    def _get_payload_body(self, payload):
        pass

    def _add_to_bit_stream(self, payload):

        # Unfortunately we can not concatenate the payload with the residual bitstream. We need to parse the NAL units
        #  and repair them before we can continue.
        self._bit_stream += self._get_payload_body(payload)
