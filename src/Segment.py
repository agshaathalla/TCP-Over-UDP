import struct
from src.SegmentFlag import SegmentFlag
from src.Flags import SYN_FLAG, ACK_FLAG, FIN_FLAG, DEF_FLAG

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

    @staticmethod
    def bytes_to_segment(segment_bytes: bytes) -> 'Segment':
        seq_num = struct.unpack('I', segment_bytes[0:4])[0]
        ack_num = struct.unpack('I', segment_bytes[4:8])[0]
        flags = SegmentFlag(segment_bytes[8])
        checksum = segment_bytes[10:12]
        payload = segment_bytes[12:]
        return Segment(seq_num, ack_num, flags, checksum, payload)
    
    def add_payload(self, payload: bytes):
        self.payload += payload
    
    def get_bytes(self) -> bytes:
        return struct.pack('iibb', self.seq_num, self.ack_num, self.flags.get_flag_bytes(), DEF_FLAG) + self.checksum + self.payload

    def __calculate_checksum(self) -> bytes:
        header = struct.pack('iibb', self.seq_num, self.ack_num, self.flags.get_flag_bytes(), DEF_FLAG)
        sum = header + self.payload
        checksum = 0
        if len(sum) % 2 != 0:
            sum += b'\x00'
        for i in range(0, len(sum), 2):
            checksum += int.from_bytes(header[i:i+2], 'big')
        while checksum >> 16:
            checksum = (checksum >> 16) + (checksum & 0xffff)
        checksum = ~checksum & 0xffff
        return checksum.to_bytes(2, 'big')
    
    def update_checksum(self):
        self.checksum = self.__calculate_checksum()

    def is_valid_checksum(self) -> bool:
        return self.checksum == self.__calculate_checksum()
    


        

if __name__ == '__main__':
    # Test Segment
    seg = Segment.syn(0)
    print(seg.get_bytes())
    print(len(seg.get_bytes()))
