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
        self.WINDOW_SIZE = 3
        print(f"[!] Client started on port {self.client_port}")

        self.connection = Connection('localhost', self.client_port)
        self.file_data = []
        

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
                    segment, address = self.connection.listen(180)
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
            syn_ack.update_checksum()
            self.connection.send(address[0], address[1], syn_ack)
            print('[!] [Handshake] SYN-ACK sent')

            # Receive ACK
            while True:
                segment, address = self.connection.listen(180)
                
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
        print("=====================================")
        segment_val = 0
        segment_err = 0
        while True:
            try:
                print(f'[!] [File Transfer] Listening for segment {segment_val}...')
                segment, address = self.connection.listen(30)
                segment = Segment.bytes_to_segment(segment)
                print(f'[!] [File Transfer] Receiving segment {segment.seq_num}...')
                # print(len(segment.get_bytes() ))

                # accepting close connection
                if segment.flags.fin:
                    print('[V] [File Transfer] FIN received')
                    segment.update_checksum()
                    print('[!] [File Transfer] Sending FIN-ACK')
                    self.connection.send('localhost', self.broadcast_port, Segment.fin_ack())
                    print('[V] [File Transfer] Closing connection')
                    break

                # Accepting new segment
                if segment.flags.syn:
                    if segment.seq_num <= segment_val:
                        print(f'[V] [File Transfer] Segment {segment.seq_num} received')
                        
                        if segment.is_valid_checksum():
                            print(f'[V] [File Transfer] Checksum valid')
                            if len(self.file_data) == segment.seq_num:
                                self.file_data.append(segment.payload)
                                segment_val += 1
                                ack = Segment.ack(segment_val, 0)
                                ack.update_checksum()
                                self.connection.send(address[0], address[1], ack)
                                print(f'[V] [File Transfer] ACK {segment_val} sent')
                                
                            print(f'[V] [File Transfer] Total segment received: {len(self.file_data)}')
                            
                        else:
                            segment_err += 1
                            print('[X] [File Transfer] Checksum invalid')
                            print('[X] [File Transfer] Retransmitting ACK...')
                        
                    else:
                        segment_err += 1
                        print(f'[X] [File Transfer] Segment {segment.seq_num} received. Expected {segment_val}')
                        ack = Segment.ack(segment_val, 0)
                        ack.update_checksum()
                        self.connection.send(address[0], address[1], ack)
                        print(f'[V] [File Transfer] ACK {segment_val} sent')

                    


                else:
                    segment = Segment.ack(segment_val, 0)
                    self.connection.send('localhost', self.broadcast_port, segment)
                    print(f"        Segment_val {segment_val} not received. Retrying...")
                    # print(segment)
                
                print('----------------------------------------------------------')

            except Exception as e:
                print(e)
                break

        write_file = open(self.file_name, 'wb')
        write_file.write(b''.join(self.file_data))
        write_file.close()


if __name__ == '__main__':
    # Parse arguments
    parser = ArgumentParser()
    parser.add_argument('client_port', type=int, help='Port to listen on')
    parser.add_argument('broadcast_port', type=int, help='Port to broadcast on')
    parser.add_argument('file_name', type=str, help='File name to write to')
    args = parser.parse_args()
    client = Client(args.client_port, args.broadcast_port, args.file_name)
    client.requesting_connection()
    client.handshake()
    client.file_transfer()