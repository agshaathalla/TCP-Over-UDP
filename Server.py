# from Node import Node
from argparse import ArgumentParser
from socket import socket
from src.Connection import Connection
from src.Segment import Segment

class Server:
    def __init__(self, port, filename):
        self.connection = Connection('localhost', port)
        print(f'[!] Server started on port {port}')
        self.filename = filename
        print(f'[!] File name: {filename}')
        self.client_ip = []
        self.client_port = []
        
    def run(self):
        pass

    def message(self, segment):
        pass

    def __handle_request(self):
        while True:
            try:
                segment, address = self.connection.listen()
                print(f'[!] [Listening] Getting Client {len(self.client_port) + 1} from port {address[1]}')

                if address[1] in self.client_port:
                    print(f'[X] [Listening] [Client {len(self.client_port) + 1}] Port {address[1]} is listed')
                    print('[X] [Listening] Retrying...')
                    continue
                segment = Segment.bytes_to_segment(segment)
                
                if segment.flags.syn:
                    print(f'[!] [Listening] [Client {len(self.client_port) + 1}] SYN received')
                    self.client_ip.append(address[0])
                    self.client_port.append(address[1])
                    break
                else:
                    print(f'[X] [Listening] [Client {len(self.client_port) + 1}] SYN not received. Retrying...')

            except socket.timeout:
                print(f'[X] [Listening] [Client {len(self.client_port + 1) + 1}] Timeout. Retrying...')

            except Exception as e:
                print(e)
                break


    def listening_connection(self):
        while True:
            print("[!] [Listening] Listening for clients...")
            self.__handle_request()
                
            answer = input('[?] [Listening] Listen more? (y/n): ')
            match answer:
                case 'y' | 'Y':
                    continue
                case 'n' | 'N':
                    break
                case _:
                    print('[X] Invalid input. Retrying...')

        print(f'[V] [Listening] Done Listening. {len(self.client_port)} clients connected')
        for i in range(len(self.client_port)):
            print(f'    [{i + 1}] {self.client_ip[i]}:{self.client_port[i]}')

    def handshake(self, client_port: int, count: int):
        print(f"[!] [Client {count}] Initiating three-way handshake with client on port {client_port}...")
        
        # Send SYN
        print(f"[!] [Client {count}] [Handshake] Sending SYN request from port {self.connection.port} to port {client_port}...")
        syn = Segment.syn(0)
        self.connection.send('localhost', client_port, syn)

        # Listening SYN-ACK
        while True:
            print(f"[!] [Client {count}] [Handshake] Listening for response from client...")
            segment, address = self.connection.listen()
            
            segment = Segment.bytes_to_segment(segment)
            if segment.flags.syn and segment.flags.ack and address[1] == client_port:
                print(f"[V] [Client {count}] [Handshake] SYN-ACK received from port {client_port}")
                break
            else:
                print(f"[X] [Client {count}] [Handshake] SYN-ACK not received. Retrying...")

        # Send ACK
        ack = Segment.ack(0, 0)
        self.connection.send('localhost', client_port, ack)
        print(f"[!] [Client {count}] [Handshake] ACK sent to port {client_port}")

    def file_transfer(self, port: int):
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
    server.listening_connection()
    for i in range(len(server.client_port)):
        server.handshake(server.client_port[i], i + 1)

