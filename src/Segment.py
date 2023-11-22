import struct
from SegmentFlag import SegmentFlag
from Flags import SYN_FLAG, ACK_FLAG, FIN_FLAG

class Segment:
    '''
    Segment class

    Attributes:
        seq_num: 4 bytes [0-3]
        ack_num: 4 bytes [4-7]
        flags: 1 byte [8]

        empty padding (for alignment): 1 byte [9]

        checksum: 2 bytes [10-11]
        payload: 32756 bytes (max) [12 - 32768]
    '''

    def __init__(self, seq_num: int, ack_num: int, flags: SegmentFlag, checksum: bytes, payload: bytes):
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags
        self.checksum = checksum
        self.payload = payload

    def __str__(self) -> str:
        return f'Segment(seq_num={self.seq_num}, ack_num={self.ack_num}, flags={self.flags}, checksum={self.checksum}, payload={self.payload})'


    @staticmethod
    def syn(seq_num: int) -> 'Segment':
        return Segment(seq_num, 0, SegmentFlag(SYN_FLAG), b'', b'')
    
    @staticmethod
    def ack(seq_num: int, ack_num: int) -> 'Segment':
        return Segment(seq_num, ack_num, SegmentFlag(ACK_FLAG), b'', b'')
    
    @staticmethod
    def syn_ack() -> 'Segment':
        return Segment(0, 0, SegmentFlag(SYN_FLAG | ACK_FLAG), b'', b'')
    
    @staticmethod
    def fin() -> 'Segment':
        return Segment(0, 0, SegmentFlag(FIN_FLAG), b'', b'')
    
    @staticmethod
    def fin_ack() -> 'Segment':
        return Segment(0, 0, SegmentFlag(FIN_FLAG | ACK_FLAG), b'', b'')
    
    # def __calculate_checksum(self) -> bytes:
        # TODO: Implement this method
    
    def update_checksum(self):
        self.checksum = self.__calculate_checksum()
        print(self.checksum)

    def is_valid_checksum(self) -> bool:
        return self.checksum == self.__calculate_checksum()
    

    def get_bytes(self) -> bytes:
        return struct.pack('I', self.seq_num) + struct.pack('I', self.ack_num) + self.flags.get_flag_bytes() + self.checksum + self.payload
        

if __name__ == '__main__':
    # Test Segment
    segment = Segment.syn(123)
    print(segment)
    print(segment.get_bytes())