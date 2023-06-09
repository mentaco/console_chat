import sys
import socket
import threading

class Server:
    def __init__(self, host_ip, host_port):
        self.host_ip = host_ip
        self.host_port = host_port
        self.bufsize = 1024
        self.connections = []
        self.lock = threading.Lock()

    def start_thread(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        soc.bind((self.host_ip, self.host_port))
        soc.listen(10)
        print(f"Listening for connections on {self.host_ip}:{self.host_port}")

        while True:
            c_soc, c_ipaddr = soc.accept()
            print(f"Accepted connection from {c_ipaddr[0]}:{c_ipaddr[1]}")
            
            self.lock.acquire()
            self.connections.append(c_soc)
            self.lock.release()

            handle_thread = threading.Thread(target=self.handle_client,
                                             args=(c_soc, c_ipaddr), daemon=True)
            handle_thread.start()

    def handle_client(self, c_soc, c_ipaddr):
        self.notify_connection(c_soc, c_ipaddr)

        while True:
            try:
                msg = c_soc.recv(self.bufsize).decode()
                if msg == "exit":
                    print(f"{c_ipaddr[0]}:{c_ipaddr[1]} exited.")
                    c_soc.close()
                    self.remove_connection(c_soc)
                    break
                self.broadcast(c_soc, c_ipaddr, msg)
            except socket.error as e:
                print(f"Failed to receive a message.\nError: {e}")
                c_soc.close()
                self.remove_connection(c_soc)
                break

    def notify_connection(self, new_conn, new_ipaddr):
        self.lock.acquire()
        for conn in self.connections:
            try:
                msg = f"{new_ipaddr[0]}:{new_ipaddr[1]} joined."
                conn.send(msg.encode())
            except socket.error as e:
                print("Faile to broadcast message.\nError: {e}")
                print(conn)
                conn.close()
        self.lock.release()

    def broadcast(self, sender, sender_ipaddr, msg):
        self.lock.acquire()
        for conn in self.connections:
            if conn != sender:
                try:
                    data = f"{sender_ipaddr[0]}:{sender_ipaddr[1]} >>" + msg
                    conn.send(data.encode())
                except socket.error as e:
                    print("Faile to broadcast message.\nError: {e}")
                    print(conn)
                    conn.close()
                    self.remove_connection(conn)
        self.lock.release()

    def remove_connection(self, conn):
        self.lock.acquire()
        if conn in self.connections:
            self.connections.remove(conn)
        self.lock.release()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <host port>\n")
    else:
        host_ip = "127.0.0.1"
        host_port = int(sys.argv[1])
        
        server = Server(host_ip, host_port)
        server.start_thread()
