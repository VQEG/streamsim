__author__ = 'Alexander Dethof'

from scapy.all import PcapReader, Packet
from os.path import exists, isfile, basename
from subtools.abstractSubTool import AbstractSubTool


class LossTraceParser(AbstractSubTool):
    """
    Loads two different pcaps and compares them. The first loaded pcap file is defined as the reference file, whereas
    the second file is defined as the loss file. Other usages may lead to undetermined results!
    """

    def __init__(self, parent):
        """
        Main initialization of this sub tool.

        :param parent: A reference to the sub tool's parent tool.
        :type parent: tool.abstractTool.AbstractTool
        """

        super(LossTraceParser, self).__init__(parent)

        self.__complete_file_path = ''
        self.__loss_file_path = ''
        self.__trace_file_path = ''

        self.__trace_file = None
        self.__loss_pcap_reader = None
        self.__complete_pcap_reader = None

    def __dump_depacketization_state(self, packet_index, packet_count):
        """
        Dumps the depacketization state, i.e. the amount of parsed packets to the total amount of packets to parse.

        :param packet_index: the index of the packet which is in process
        :type packet_index: int

        :param packet_count: the total amount of packet to process
        :type packet_count: int
        """

        assert isinstance(packet_index, int)
        assert isinstance(packet_count, int)

        if packet_index > 1:
            self.remove_last_output()

        print '[%s] Process packet: %d/%d' % (basename(self.__trace_file_path), packet_index, packet_count)

    def set_complete_file_path(self, complete_file_path):
        """
        Sets the path of the file, which is complete.

        :param complete_file_path: path of the complete packet capture
        :type complete_file_path: basestring

        :return: self
        :rtype: LossTraceParser
        """

        assert isinstance(complete_file_path, basestring)
        assert isfile(complete_file_path) and exists(complete_file_path)

        self.__complete_file_path = complete_file_path
        self.__complete_pcap_reader = PcapReader(complete_file_path)
        return self

    def set_loss_file_path(self, loss_file_path):
        """
        Sets the file which consists of the loss.

        :param loss_file_path: the path of the file consisting loss
        :type loss_file_path: basestring

        :return: self
        :rtype: LossTraceParser
        """

        assert isinstance(loss_file_path, basestring)
        assert isfile(loss_file_path) and exists(loss_file_path)

        self.__loss_file_path = loss_file_path
        self.__loss_pcap_reader = PcapReader(loss_file_path)
        return self

    def set_trace_file_path(self, trace_file_path):
        """
        Sets the path of the file where the trace should be stored in.

        :param trace_file_path: the path of the file where the trace should be stored in
        :type trace_file_path: basestring

        :return: self
        :rtype: LossTraceParser
        """

        assert isinstance(trace_file_path, basestring)

        self.__trace_file_path = trace_file_path
        return self

    def trace(self):
        """
        Generates a trace file at the given path in Telchemy-CSV-Style, i.e. each row represents a packet in the
         complete pcap stream. The value written in (1 or 0) delivers information if the packet is part of the loss
          stream or not.
        """

        assert isinstance(self.__complete_pcap_reader, PcapReader)
        assert isinstance(self.__loss_pcap_reader, PcapReader)
        assert self.__trace_file_path

        # open trace file and make it clear after that add pcap states for each individual packet
        self.__trace_file = open(self.__trace_file_path, 'a')
        self.__trace_file.flush()

        # go through the pcaps and compare them
        last_incomplete_packet = None
        packet_count = 0  # TODO len(self.__complete_pcap_reader)
        packet_index = 1
        for complete_packet in self.__complete_pcap_reader:
            assert isinstance(complete_packet, Packet)

            if last_incomplete_packet is None:
                try:
                    loss_packet = self.__loss_pcap_reader.next()
                except StopIteration:
                    loss_packet = None
            else:
                loss_packet = last_incomplete_packet

            if isinstance(loss_packet, Packet) and loss_packet.payload == complete_packet.payload:
                is_packet_complete = True
                last_incomplete_packet = None
            else:
                is_packet_complete = False
                last_incomplete_packet = loss_packet

            self.__trace_file.write(str(int(is_packet_complete)) + "\n")
            self.__dump_depacketization_state(packet_index, packet_count)
            packet_index += 1

    def cleanup(self):
        """
        Cleans up the tool.
        """

        if isinstance(self.__trace_file, file):
            self.__trace_file.close()

