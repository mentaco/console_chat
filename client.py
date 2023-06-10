import sys
import socket
import threading
import curses

class Client:
    def __init__(self, s_ipaddr, s_port):
        self.s_ipaddr = s_ipaddr
        self.s_port = s_port
        self.bufsize = 1024
    
    def start_chat(self, stdscr):
        height, width = stdscr.getmaxyx()
        input_h = 3
        content_win = curses.newwin(height-input_h, width, 0, 0)
        input_win = curses.newwin(input_h, width, height-input_h-1, 0)
        content_win.addstr("[Chat room]\n")

        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            soc.connect((self.s_ipaddr, self.s_port))
            content_win.addstr("Connected to chat server.\n")
        except socket.error as e:
            content_win.addstr(f"Failed to connect to chat server.\nError: {e}\n")

        content_win.refresh()

        recv_threed = threading.Thread(target=self.receive_msg,
                                       args=(content_win, soc), daemon=True)
        send_thread = threading.Thread(target=self.send_msg,
                                      args=(content_win, input_win, soc), daemon=True)
        recv_threed.start()
        send_thread.start()
        recv_threed.join()
        send_thread.join()

        curses.endwin()

    def receive_msg(self, content_win, soc):
        while True:
            try:
                msg = soc.recv(self.bufsize).decode()
                content_win.addstr(f"{msg}\n")
            except socket.error as e:
                content_win.addstr(f"Failed to receive a message.\nError: {e}\n")
                soc.close()
                break
            content_win.refresh()

    def send_msg(self, content_win, input_win, soc):
        curses.echo()
        input_win.keypad(True)

        while True:
            input_win.clear()
            input_win.box()
            input_win.addstr(0, 2, "[INPUT]")
            input_win.addstr(1, 1, " >> ")
            input_win.refresh()

            input_win.move(1, 5)
            msg = input_win.getstr().decode()

            if msg:
                content_win.addstr(f">> {msg}\n")
                content_win.refresh()

                try:
                    if msg == "exit":
                        soc.send(msg.encode())
                        soc.close()
                        break
                    soc.send(msg.encode())
                except socket.error as e:
                    content_win.addstr(f"Failed to send a message.\nError: {e}")
                    soc.close()
                    break


if __name__ == '__main__':
    if len(sys.argv) != 2:
        stdscr.addstr(f"Usage: python3 {sys.argv[0]} <server port>\n")
    else:
        s_ipaddr = "127.0.0.1"
        s_port = int(sys.argv[1])

        client = Client(s_ipaddr, s_port)
        curses.wrapper(client.start_chat)
