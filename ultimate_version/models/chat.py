import socket
class Chat():
    def __init__(self, host, port):
        self.host = str(host)
        self.port = int(port)
        self.socket = socket.socket()

    def send_message(self, msg):
        self.socket = socket.socket()
        self.socket.connect((self.host, self.port))
        self.socket.sendall(msg.encode())
        return self.retrieve_message()

    def retrieve_message(self):
        msg = self.socket.recv(1024)
        self.socket.close()
        return msg.decode('utf-8')