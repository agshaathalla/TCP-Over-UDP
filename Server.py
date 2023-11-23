# from Node import Node
from argparse import ArgumentParser
from src.Connection import Connection
from src.Segment import Segment

class Server:
    def __init__(self, port, filename):
        self.connection = Connection('localhost', port)
        print(f'[!] Server started on port {port}')
        self.filename = filename
        print(f'[!] File name: {filename}')
        self.ip = []
        self.port = []
        self.countConnection = 0
        
    def run(self):
        pass

    def message(self, segment):
        pass

    def three_way_handshake(self):
        print("[!] [Handshake] Listening for clients...")
        count = 0
        while True:
            print(f'[!] [Handshake] Handshake to clinet {count + 1}')
            # Receive SYN
            while True:
                segment, address = self.connection.listen()
                segment = Segment.bytes_to_segment(segment)
                # print(segment)
                if segment.flags.syn:
                    print(f'[!] [Handshake] [Client {count + 1}] SYN received')
                    break
            
            # Send SYN-ACK
            syn_ack = Segment.syn_ack()
            self.connection.send(address[0], address[1], syn_ack)
            print(f'[!] [Handshake] [Client {count + 1}] SYN-ACK sent')

            # Receive ACK
            while True:
                segment, address = self.connection.listen()
                
                segment = Segment.bytes_to_segment(segment)
                if segment.flags.ack:
                    print(f'[!] [Handshake] [Client {count + 1}] ACK received')
                    count += 1
                    self.countConnection += 1
                    self.ip.append(address[0])
                    self.port.append(address[1])
                    break
            answer = input('[?] Listen more? (y/n): ')
            if answer == 'n' or answer == 'N':
                break

        print(f'ip: {self.ip}')
        print(f'port: {self.port}')



    def file_transfer(self):
        '''
        Server as Sender
        '''
        segment = Segment.syn(0) # [DELETE] dummy segment
        seq_val = 0
        seq_base = 0
        seq_max = self.WINDOW_SIZE - 1
        while True:
            while seq_base <= seq_val <= seq_max:
                segment = Segment.syn(seq_val)
                # [CODE] send file
                # [CODE] send segment
                seq_val += 1

            if segment.seq_num > seq_base:
                seq_max = (seq_max - seq_base) + segment.seq_num
                seq_base = segment.seq_num
                break
            
            if seq_base <= segment.seq_num <= seq_max:
                break

            # Receive ack from client
            try:
                # [CODE] listening segment
                segment = Segment.ack(0, 0) # [DELETE] dummy segment
                if segment.flags.ack:
                    # [CODE] write file
                    # [CODE] send fin_ack (dummy fin_ack)
                    seq_base = segment.ack_num + 1
                    seq_max = seq_base + self.WINDOW_SIZE - 1
                else:
                    raise ValueError('Not ACK')
            except Exception as e:
                print(e)
                break
        
        # File transfer done
        # [CODE] close connection

if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument('broadcast_port', type=int, help='Port to broadcast on')
    parser.add_argument('file_name', type=str, help='File name to write to')
    args = parser.parse_args()
    server = Server(args.broadcast_port, args.file_name)
    server.three_way_handshake()
