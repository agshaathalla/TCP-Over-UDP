from argparse import ArgumentParser
from src.Connection import Connection
from src.Segment import Segment
from src.Flags import FIN_FLAG, SYN_FLAG, ACK_FLAG

class Client:
    def __init__(self, client_port, broadcast_port, file_name):
        self.client_port = client_port
        self.broadcast_port = broadcast_port
        self.file_name = file_name
        self.conn = Connection('localhost', self.client_port)
        self.countACK = 0
        print(f"[!] Client started on port {self.client_port}")
        

    def listen(self):
        pass

    def write(self):
        pass

    def close(self):
        pass

    def three_way_handshake(self):
        print(f"[!] Initiating three-way handshake...")
        print(f"[!] [Handshake] [Client] Listening for server...")
        # Send SYN
        print(f"[!] [Handshake] [Client] Sending SYN request from port {self.client_port}")
        syn = Segment.syn(0)
        self.conn.send('localhost', self.broadcast_port, syn)
        # print("SYN sent successfully!")
        while True:
            # Receive SYN-ACK
            segment, address = self.conn.listen()
            # print(address)
            segment = Segment.bytes_to_segment(segment)
            # print(segment)
            if segment.flags.syn and segment.flags.ack:
                break
        # Send ACK
        ack = Segment.ack(0, 0)
        self.conn.send('localhost', self.broadcast_port, ack)
        self.countACK += 1
        print(f"[Segment SEQ = {self.countACK} Received, ACK sent]")



    def file_transfer(self):
        '''
        Client as Receiver
        '''
        segment = Segment.syn(0) # [DELETE] dummy segment
        segment_val = 0
        while True:
            try:
                # [CODE] listening segment
                if segment.flags.fin:
                    # [CODE] write file
                    # [CODE] send fin_ack (dummy fin_ack)
                    break

                # Accepting new segment
                if segment.seq_num == segment_val:
                    pass # [DELETE] dummy code
                    # [CODE] handle file

                else:
                    # tolak segmen
                    break
                segment = Segment.ack(0, segment_val)
                segment_val += 1

            except Exception as e:
                print(e)
                break



if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument('client_port', type=int, help='Port to listen on')
    parser.add_argument('broadcast_port', type=int, help='Port to broadcast on')
    parser.add_argument('file_name', type=str, help='File name to write to')
    args = parser.parse_args()

    # print(args.server_port)
    # print(args.server_ip)
    # print(args.file_name)
    # conn = Connection('localhost', 8000)
    # conn.listen()
    client = Client(args.client_port, args.broadcast_port, args.file_name)
    client.three_way_handshake()