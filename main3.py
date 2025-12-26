import socket
import execute_commands

HOST = ''
PORT = 6379


def resp_parser(data):
    '''
    The RESP parser will ensure the RESP frame received is complete before being processed.
    Returns 2 variables: 1)complete list of args for a RESP frame sent and 2) any leftover frame
    '''
    print('resp parser execution started')
    if not data.startswith(b'*'):
       raise ValueError("Invalid RESP frame: must start with '*'")

    print("first printing data received", data)
    #split the received frame into a list and remove trailing empty string
    lines = data.split(b'\r\n')
    if lines and lines[-1]==b'':
          lines = lines[:-1]
    print("list of byte strings gotten from splitting resp frame",lines)
    
    #at least 3 elements must be present in the list holding the RESP frame if it has one argument
    if len(lines) < 3:
       raise ValueError("Incomplete RESP frame")
    
    #Get the number of arguments from the first element in 'lines' list
    arg_count_line = lines[0]
    try:
        arg_count = int(arg_count_line[1:]) #skip the '*'
        print(f'arg_count is {arg_count}')
    except:
        raise ValueError("Invalid argument count")
    
    #use 'arg_count' to determine if the RESP frame is received completely. 
    num_expected_args = 1 + arg_count * 2 
    if len(lines) < num_expected_args:
       raise ValueError("Incomplete RESP frame, wait for more data ...")
   
    args = []
    i = 1
    while i < num_expected_args:
        data_line = lines[i+1]
        args.append(data_line)
        i+=2
        
    #if length of the buffer received is greater than expected length, then we may have received additional frames
    complete_frame_parsed = b"\r\n".join(lines[:num_expected_args]) + b"\r\n"
    print('complete frame parsed based on arg count',complete_frame_parsed)
    leftover_frame =  data[len(complete_frame_parsed):]
    print('left over frame:', leftover_frame)
    print(args)
    return args, leftover_frame
 

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
  
   #while the incoming connection is opened, get data sent from client and store in a buffer. process the message sent
   with conn_sock:
     while True:
       try: 
          data = conn_sock.recv(1024)
          if not data:
            print("client disconnected!")
            break
          buffer +=data
          print(f"received data so far: {buffer.decode().strip().upper()}")
        
          try:
            print('executing the resp parser now') 
            resp_args, leftover = resp_parser(buffer)
            print(resp_args)
            if leftover: 
              print('leftover:',leftover)
            
          except Exception as e:
            print(f"parsing Error: {e}")
            continue
    
        #handle message received 
          value_to_send = execute_commands.execute_commands(resp_args)
          conn_sock.sendall(value_to_send)
        #set buffer to any leftover arg from latest parsed frame after getting all of the last received command
          buffer = leftover
              
       except Exception as ex:
         print(f"Exception: {ex}")
         print("Client disconnected. Connection ended abruptly")
         break
            
