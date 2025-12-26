#basic tcp server to listen and accept connection and send data
import socket

HOST = ''
PORT = 6379
#create a socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listening_socket:

#reuse the port immediately after connection is closed
   listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

   #Bind the listening socket to host and port
   listening_socket.bind((HOST, PORT))
   listening_socket.listen(2)

   #accept client connection 
   print("waiting for incoming connection")
   conn_sock, addr = listening_socket.accept()
   print(f"new connection accepted: connection socket is {conn_sock}")
   print(f"connected by:{addr}")
   buffer = b""
   command = ""
   #while the incoming connection is opened, get data sent from client and store in a buffer. process the command
   # when the user presses the Enter key(or newline)
   with conn_sock:
    while True:
        try: 
          data = conn_sock.recv(1024)
          if not data:
            print("client disconnected!")
            break
          buffer +=data
          print(f"received data so far: {buffer.decode().upper()}")
        
          if b"\r\n" not in buffer:
             continue            
          command += buffer.decode().upper()
          print(f"Received:{command}") 
        
          #reset buffer to empty after handling last command
          buffer = b""
          if command =="PING":
            conn_sock.sendall(b"+PONG\r\n")
          elif command == "ECHO":
            conn_sock.sendall(b"+ECHO\r\n")
          else:
            print(f"Unknown command{command}")
        except ConnectionResetError:
            print("Connection ended abruptly")







