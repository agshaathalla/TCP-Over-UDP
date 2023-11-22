import struct
from Flags import SYN_FLAG, ACK_FLAG, FIN_FLAG

class SegmentFlag:
    '''
    SegmentFlag class
    
    Attributes:
        syn: bit 1
        ack: bit 4
        fin: bit 0
    '''

    def __init__(self, flag: bytes):
        '''
        Initializes a SegmentFlag object with the given 1-byte flag representation.
        '''
        self.syn = True if flag & SYN_FLAG else False
        self.ack = True if flag & ACK_FLAG else False
        self.fin = True if flag & FIN_FLAG else False

    def __str__(self) -> str:
        '''
        Returns a string representation of this SegmentFlag object.
        '''
        return 'SYN: ' + str(self.syn) + '\nACK: ' + str(self.ack) + '\nFIN: ' + str(self.fin)

    def get_flag_bytes(self) -> bytes:
        '''
        Returns the 1-byte flag representation of this SegmentFlag object.
        '''
        return struct.pack('?', self.syn) + struct.pack('?', self.ack) + struct.pack('?', self.fin)
    
if __name__ == '__main__':
    # Test SegmentFlag
    flag = SegmentFlag(SYN_FLAG | ACK_FLAG)
    print(flag.syn)
    print(flag.ack)
    print(flag.fin)
    print(flag.get_flag_bytes())