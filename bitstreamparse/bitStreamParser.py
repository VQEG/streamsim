__author__ = 'Alexander Dethof'


from abc import ABCMeta, abstractmethod


class BitStreamParser(object):

    __metaclass__ = ABCMeta

    def __init__(self, pcap_file_path):

        self._bit_stream = ''
        self._pcap_file_path = pcap_file_path
        self._init_class_variables()

        self._parse_pcap_file()

    @staticmethod
    def _dump_packet_index(packet_index, packet_count):
        """
        Dumps the parsing state of a pcap file.

        :param packet_index: the index of the packet which is opened
        :type packet_index: int

        :param packet_count: the number of total packets to parse
        :type packet_count: int
        """

        assert isinstance(packet_index, int)
        assert isinstance(packet_count, int)

        if packet_index > 1:
            from cmd.operator import Operator
            Operator.remove_last_output()

        print 'Parse packet: %d/%d' % (packet_index, packet_count)

    @abstractmethod
    def _init_class_variables(self):
        """
        TODO
        :return:
        """

        pass

    def _parse_pcap_file(self):

        self._before_parsing()

        from scapy.all import rdpcap
        self._packets = rdpcap(self._pcap_file_path)

        self._parse_packets()

        self._after_parsing()

    def _parse_packets(self):

        packet_count = len(self._packets)
        packet_index = 1

        for packet in self._packets:

            self._dump_packet_index(packet_index, packet_count)

            # noinspection PyBroadException
            # try:
            self._parse_packet(packet)
            # except: pass

            packet_index += 1

    def get_bit_stream(self):
        """
        Returns the bit stream extracted from the parsed packets
        :return bit stream extracted from the parsed packets
        """

        return self._bit_stream

    @abstractmethod
    def _parse_packet(self, packet):
        """
        This method can be used to parse a singular packet into the bitstream

        :param packet: the packet to parse
        :type packet: Packet
        """

        pass

    @abstractmethod
    def _before_parsing(self):
        """
        Use this method to execute code before all packets are parsed
        """

        print 'No bounding!'

    @abstractmethod
    def _after_parsing(self):
        """
        Use this method to execute code after all packets were parsed
        """

        print 'No splitting!'
