import socket

def send_message():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
           sock.connect(('localhost', 6379))
           #build RESP frame
           msg = (f"*3\r\n"
                  f"$3\r\n"
                  f"DEL\r\n"
                  f"$14\r\n"
                  f"Game Top Score\r\n"
                  f"$10\r\n"
                  f"Top scorer\r\n").encode('utf-8')

           sock.sendall(msg)
           response = sock.recv(1024)
           if not response:
                print("Server disconnected!")
           print("Response:", response)
        except:
           print("No server listening or Connection ended abruptly")

send_message()