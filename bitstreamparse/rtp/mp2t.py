__author__ = 'Alexander Dethof'

from bitstreamparse.bitStreamParser import BitStreamParser
from scapy.all import Packet
from scapy.layers.inet import UDP
from scapy.layers.rtp import RTP, Raw


class Mp2t(BitStreamParser):

    MP2TS_PAYLOAD_TYPE_ID = 33

    def _init_class_variables(self):
        self._ssrc_id = None
        self._payload_type = None

    def _parse_packet(self, packet):
        """
        Parses the RTP/MP2T packet into the bitstream

        :param packet: the packet to parse
        :type packet: Packet
        """

        assert isinstance(packet, Packet), 'The given packet variable is not a valid Scapy packet!'
        assert packet.haslayer(RTP), 'Packet does not contain any RTP layer!'
        assert packet.haslayer(Raw), 'Packet does not contain any payload!'

        # RTP/MP2T packets can be concatenated but only if the payload type is valid and they belong to the same SSRC

        # Extract header information
        payload_type = int(packet[RTP].getfieldval('payload'))
        ssrc_id = int(packet[RTP].getfieldval('sourcesync'))

        # the payload type needs to indicate to be MP2T
        if payload_type == self.MP2TS_PAYLOAD_TYPE_ID:

            if self._payload_type is None:  # no payload type set yet
                self._payload_type = payload_type

            if self._ssrc_id is None:  # no SSRC ID set yet
                self._ssrc_id = ssrc_id

            # We can only concatenate if we follow the correct payload number and ssrc id
            if payload_type == self._payload_type and ssrc_id == self._ssrc_id:
                self._bit_stream += packet[Raw].load

    # noinspection PyMethodMayBeStatic
    def _before_parsing(self):
        """
        Before all packets are parsed we need to assure that after the UDP layer follows directly the raw payload
        """

        from scapy.all import bind_layers
        bind_layers(UDP, RTP)

    # noinspection PyMethodMayBeStatic
    def _after_parsing(self):
        """
        After the parsing was done we need to split up the layering again
        """

        from scapy.all import split_layers
        split_layers(UDP, RTP)