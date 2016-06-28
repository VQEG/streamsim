__author__ = 'Alexander Dethof'

from bitstreamparse.rtpParser import RtpParser


class RawVideo(RtpParser):

    DYNAMIC_PAYLOAD_TYPE_ID_MIN = 96
    DYNAMIC_PAYLOAD_TYPE_ID_MAX = 96

    def _is_valid_payload_type(self, payload_type):
        assert isinstance(payload_type, int), 'Invalid payload type given!'

        return self.DYNAMIC_PAYLOAD_TYPE_ID_MIN <= payload_type <= self.DYNAMIC_PAYLOAD_TYPE_ID_MAX

    def _add_to_bit_stream(self, payload):
        self._bit_stream += payload
