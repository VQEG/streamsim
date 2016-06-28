__author__ = 'Alexander Dethof'

from bitstreamparse.bitStreamParser import BitStreamParser
from scapy.all import Packet
from scapy.layers.inet import UDP, Raw


class Mp2t(BitStreamParser):

    def _init_class_variables(self):
        pass

    def _parse_packet(self, packet):
        """
        Parses the UDP/MP2T packet into the bitstream

        :param packet: the packet to parse
        :type packet: Packet
        """

        assert isinstance(packet, Packet), 'The given packet variable is not a valid Scapy packet!'
        assert packet.haslayer(Raw), 'Packet does not contain any payload!'

        # UDP/MP2T packets can just be concatenated
        self._bit_stream += packet[Raw].load

    # noinspection PyMethodMayBeStatic
    def _before_parsing(self):
        """
        Before all packets are parsed we need to assure that after the UDP layer follows directly the raw payload
        """

        from scapy.all import bind_layers
        bind_layers(UDP, Raw)

    # noinspection PyMethodMayBeStatic
    def _after_parsing(self):
        """
        After the parsing was done we need to split up the layering again
        """

        from scapy.all import split_layers
        split_layers(UDP, Raw)