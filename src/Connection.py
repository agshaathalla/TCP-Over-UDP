import socket
from src.MessageInfo import MessageInfo
from src.Segment import Segment
class Connection:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, self.port))
        print("Connection created successfully!")
    
    def send(self, ip_remote: str, port_remote: int, msg: Segment):
            self.socket.sendto(msg.get_bytes(), (ip_remote, port_remote))
            print("Data sent successfully!")

    def listen(self):
            self.socket.settimeout(20)
            data, addr = self.socket.recvfrom(32756)
            print(data.decode("utf-8"))
            return data, addr 
    
    def close(self):
        self.socket.close()
    
    def register_handler(self, handler: callable(MessageInfo)):
        self.handler = handler
    
    def notify(self):
        print(f"ip: {self.ip}, port: {self.port}, handler: {self.handler}")

