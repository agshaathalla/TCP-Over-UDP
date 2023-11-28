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
        self.file = self.file_partition()
        self.WINDOW_SIZE = 3

    def file_partition(self):
        file = open(self.filename, 'rb').read()
        # print(len(file))
        array_of_content = []
        while len(file) >= 32756:
            array_of_content.append(file[:32756])
            file = file[32756:]
        if len(file) > 0:
            array_of_content.append(file)
        return array_of_content

    def __handle_request(self):
        while True:
            try:
                print("[!] [Listening] Listening for clients...")
                segment, address = self.connection.listen(20)
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

            except TimeoutError:
                print(f'[X] [Listening] Timeout. Retrying...')
                answer = input('[?] [Listening] Listen more? (y/n): ')
                while answer not in ['y', 'n']:
                    print('[X] [Listening] Invalid answer')
                    answer = input('[?] [Listening] Listen more? (y/n): ')

                match answer:
                    case 'y':
                        continue
                    case 'n':
                        break

            except Exception as e:
                print(e)
                break


    def listening_connection(self):
        while True:
            self.__handle_request()
                
            answer = input('[?] [Listening] Listen more? (y/n): ')
            while answer not in ['y', 'n']:
                print('[X] [Listening] Invalid answer')
                answer = input('[?] [Listening] Listen more? (y/n): ')

            match answer:
                case 'y':
                    continue
                case 'n':
                    break

        print(f'[V] [Listening] Done Listening. {len(self.client_port)} clients connected')
        for i in range(len(self.client_port)):
            print(f'    [{i + 1}] {self.client_ip[i]}:{self.client_port[i]}')
            

    def handshake(self, client_port: int, count: int):
        print("=====================================")
        print(f"[!] [Client {count}] Initiating three-way handshake with client on port {client_port}...")
        
        # Send SYN
        print(f"[!] [Client {count}] [Handshake] Sending SYN request from port {self.connection.port} to port {client_port}...")
        syn = Segment.syn(0)
        syn.update_checksum()
        self.connection.send('localhost', client_port, syn)

        # Listening SYN-ACK
        while True:
            print(f"[!] [Client {count}] [Handshake] Listening for response from client...")
            segment, address = self.connection.listen(9999)
            
            segment = Segment.bytes_to_segment(segment)
            if segment.flags.syn and segment.flags.ack and address[1] == client_port:
                print(f"[V] [Client {count}] [Handshake] SYN-ACK received from port {client_port}")
                break
            else:
                print(f"[X] [Client {count}] [Handshake] SYN-ACK not received. Retrying...")

        # Send ACK
        ack = Segment.ack(0, 0)
        ack.update_checksum()
        self.connection.send('localhost', client_port, ack)
        print(f"[!] [Client {count}] [Handshake] ACK sent to port {client_port}")
        

    def file_transfer(self, port: int):
        '''
        Server as Sender
        '''
        print("=====================================")
        print(f'[!] Initiating file transfer to client on port {port}')

        seq_val = 0
        seq_base = 0
        seq_max = self.WINDOW_SIZE - 1      # NOTE kalau si spek itu di + 1
        while True:
            # Sending Segment
            while seq_base <= seq_val <= seq_max and seq_val < len(self.file):
                print(f'[!] [Client {port}] [Transfer] Sending segment {seq_val}')
                segment = Segment.syn(seq_val)
                segment.add_payload(self.file[seq_val])
                segment.update_checksum()
                self.connection.send('localhost', port, segment)
                seq_val += 1

            if seq_val >= len(self.file):
                print(f'[V] [Client {port}] [Transfer] File transfer done')
                break

            

            # Listening for ack from client
            try:
                print(f'[!] [Client {port}] [Transfer] Listening for ACK from client...')
                segment, _ = self.connection.listen(5)
                segment = Segment.bytes_to_segment(segment)

                # Updating seq_max and seq_base
                if segment.flags.ack:
                    if (segment.seq_num > seq_base):
                        print(f'[V] [Client {port}] [Transfer] ACK {segment.seq_num} received')
                        seq_max = (seq_max - seq_base) + segment.seq_num
                        seq_base = segment.seq_num

                    else:
                        print(f'[X] [Client {port}] [Transfer] ACK {segment.seq_num} received')
                        print(f'[X] [Client {port}] [Transfer] Retransmitting segment {segment.seq_num}')
                        seq_val = segment.seq_num
                        seq_base = seq_val
                        seq_max = seq_base + self.WINDOW_SIZE - 1
                else:
                    raise ValueError('ACK not received')
                
            except TimeoutError:
                print(f'[X] [Client {port}] [Transfer] Timeout. Retry sending segment {seq_val - 1}')
                pass

            except ValueError as e:
                print(f'[X] [Client {port}] [Transfer] {e}')
                continue

            print('----------------------------------------------------------')

        
        
    def close_connection(self, port: int):
        print("=====================================")
        print("[!] Closing connection...")
        while True:
            print(f'[!] [Client {port}] [Closing] Sending FIN')
            self.connection.send('localhost', port, Segment.fin())
            print(f'[!] [Client {port}] [Closing] Listening for FIN-ACK')
            try:
                segment, _ = self.connection.listen(5)
                segment = Segment.bytes_to_segment(segment)
                if segment.flags.fin and segment.flags.ack:
                    print(f'[V] [Client {port}] [Closing] FIN-ACK received')
                    break
                else:
                    raise ValueError('Not FIN-ACK')
            except Exception as e:
                print(e)
                print(f'[X] [Client {port}] [Closing] FIN-ACK not received. Retrying...')
                continue
        print(f'[V] [Client {port}] [Closing] Connection closed\n\n')

    def server_main(self):
        self.listening_connection()
        for i in range(len(self.client_port)):
            self.handshake(self.client_port[i], i + 1)
            self.file_transfer(self.client_port[i])
            self.close_connection(self.client_port[i])
        

if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument('broadcast_port', type=int, help='Port to broadcast on')
    parser.add_argument('file_name', type=str, help='File name to write to')
    args = parser.parse_args()

    server = Server(args.broadcast_port, args.file_name)
    server.server_main()
