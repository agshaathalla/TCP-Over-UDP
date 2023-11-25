from argparse import ArgumentParser
from socket import socket
from src.Connection import Connection
from src.Segment import Segment
from src.Flags import FIN_FLAG, SYN_FLAG, ACK_FLAG

class Client:
    def __init__(self, client_port, broadcast_port, file_name):
        self.client_port = client_port
        self.broadcast_port = broadcast_port
        self.file_name = file_name
        self.countACK = 0
        print(f"[!] Client started on port {self.client_port}")

        self.connection = Connection('localhost', self.client_port)
        

    def listen(self):
        pass

    def write(self):
        pass

    def close(self):
        pass

    def requesting_connection(self):
        req_segment = Segment.syn(0)
        self.connection.send('localhost', self.broadcast_port, req_segment)

    def handshake(self):
        while True:
            print("[!] [Handshake] Waiting for server...")

            # Receive SYN
            while True:
                try:
                    segment, address = self.connection.listen()
                    print(f'[!] [Handshake] Received handshake from server on port {address[1]}')

                    if address[1] != self.broadcast_port:
                        print(f'[X] [Handshake] Wrong port. Retried listening for server on port {self.broadcast_port}...')
                        continue
                    segment = Segment.bytes_to_segment(segment)
        
                    if segment.flags.syn:
                        print('[!] [Handshake] SYN received')
                        break
                    else:
                        print('[X] [Handshake] SYN not received. Retrying...')

                except socket.timeout:
                    print('[X] [Handshake] Timeout. Retrying...')
                    continue
                    
                except Exception as e:
                    print(f'[X] [Handshake] {e}')
                    print('[X] [Handshake] Retrying...')
                    continue
            
            # Send SYN-ACK
            syn_ack = Segment.syn_ack()
            self.connection.send(address[0], address[1], syn_ack)
            print('[!] [Handshake] SYN-ACK sent')

            # Receive ACK
            while True:
                segment, address = self.connection.listen()
                
                segment = Segment.bytes_to_segment(segment)
                if segment.flags.ack:
                    print('[!] [Handshake] ACK received')
                    break
                else:
                    print('[X] [Handshake] ACK not received. Retrying...')
            break

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
    # connection = Connection('localhost', 8000)
    # connection.listen()
    client = Client(args.client_port, args.broadcast_port, args.file_name)
    client.requesting_connection()
    client.handshake()