import socket
import sys

def send_message():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
           sock.connect(('localhost', 6379))
           #build RESP frame
           msg = (f"*2\r\n"
                  f"$3\r\n"
                  f"GET\r\n"
                  f"$14\r\n"
                  f"Game Top Score\r\n"
                  ).encode('utf-8')

           sock.sendall(msg)
           response = sock.recv(1024)
           if not response:
                print("Server disconnected!")
           print("Response:", response.decode('utf-8'))
        except:
           print('Error', sys.exc_info())
           print("No server listening or Connection ended abruptly")

send_message()