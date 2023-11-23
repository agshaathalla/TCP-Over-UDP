import struct
from src.Flags import SYN_FLAG, ACK_FLAG, FIN_FLAG, DEF_FLAG

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
        flag = DEF_FLAG
        flag |= SYN_FLAG if self.syn else 0
        flag |= ACK_FLAG if self.ack else 0
        flag |= FIN_FLAG if self.fin else 0
        return flag
    
if __name__ == '__main__':
    # Test SegmentFlag
    flag = SegmentFlag(SYN_FLAG | ACK_FLAG)
    print(flag.syn)
    print(flag.ack)
    print(flag.fin)
    print(flag.get_flag_bytes())