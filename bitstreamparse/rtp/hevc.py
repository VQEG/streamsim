__author__ = 'Alexander Dethof'

from bitstreamparse.rtp.rawVideo import RawVideo
from util.bitparse import str_to_bits, bits_to_int


class Hevc(RawVideo):

    def _parse_nal_unit(self, nal_unit_str):
        assert isinstance(nal_unit_str, basestring)
        assert len(nal_unit_str) == 2

        # NAL Unit structure:
        #  https://tools.ietf.org/html/rfc7798#section-1.1.4
        nal_unit_bits = str_to_bits(nal_unit_str)

        # +---------------+---------------+
        # |0|1|2|3|4|5|6|7|0|1|2|3|4|5|6|7|
        # +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
        # |F|   Type    |  LayerId  | TID |
        # +-------------+-----------------+
        nal_unit = dict()

        # F: 1 bit
        # forbidden_zero_bit.  Required to be zero in [HEVC].  Note that the
        # inclusion of this bit in the NAL unit header was to enable
        # transport of HEVC video over MPEG-2 transport systems (avoidance
        # of start code emulations) [MPEG2S].  In the context of this memo,
        # the value 1 may be used to indicate a syntax violation, e.g., for
        # a NAL unit resulted from aggregating a number of fragmented units
        # of a NAL unit but missing the last fragment, as described in
        # Section 4.4.3.
        nal_unit[self.NAL_UNIT_FIELD_FORBIDDEN] = nal_unit_bits[0]

        # Type: 6 bits
        # nal_unit_type.  This field specifies the NAL unit type as defined
        # in Table 7-1 of [HEVC].  If the most significant bit of this field
        # of a NAL unit is equal to 0 (i.e., the value of this field is less
        # than 32), the NAL unit is a VCL NAL unit.  Otherwise, the NAL unit
        # is a non-VCL NAL unit.  For a reference of all currently defined
        # NAL unit types and their semantics, please refer to Section 7.4.2
        # in [HEVC].
        nal_unit[self.NAL_UNIT_FIELD_TYPE] = bits_to_int(nal_unit_bits[1:6])

        # LayerId: 6 bits
        # nuh_layer_id.  Required to be equal to zero in [HEVC].  It is
        # anticipated that in future scalable or 3D video coding extensions
        # of this specification, this syntax element will be used to
        # identify additional layers that may be present in the CVS, wherein
        # a layer may be, e.g., a spatial scalable layer, a quality scalable
        # layer, a texture view, or a depth view.
        nal_unit[self.NAL_UNIT_FIELD_LAYER_ID] = bits_to_int(nal_unit_bits[7:12])

        # TID: 3 bits
        # nuh_temporal_id_plus1.  This field specifies the temporal
        # identifier of the NAL unit plus 1.  The value of TemporalId is
        # equal to TID minus 1.  A TID value of 0 is illegal to ensure that
        # there is at least one bit in the NAL unit header equal to 1, so to
        # enable independent considerations of start code emulations in the
        # NAL unit header and in the NAL unit payload data.
        nal_unit[self.NAL_UNIT_FIELD_TID] = bits_to_int(nal_unit_bits[13:16])

        return nal_unit

    def _parse_payload_header(self, payload_header):
        return self._parse_nal_unit(payload_header)

    def _get_payload_body(self, payload):

        # We parse the payload as described in RFC 7798
        # https://tools.ietf.org/html/rfc7798

        payload_header_str = payload[0:2]
        print payload_header_str

        print map(lambda byte: int(byte), bytearray(payload_header_str))

        # The first two bytes of a packet's payload form the RTP payload header
        payload_header = self._parse_payload_header(payload_header_str)

        print payload_header
        print '-- DEL --'

        return '\0\0\0\0\0\0\0\1' + payload


