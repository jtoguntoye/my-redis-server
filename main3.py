import socket
import select
import execute_commands
import errno

HOST = ''
PORT = 6379

#dictionary to store clients #sockets -> read_buffer
clients = {}

#create global listening socket and connection sockets
listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#reuse the port immediately after connection is closed
listening_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 

#Bind the listening socket to host and port
listening_socket.bind((HOST, PORT))
listening_socket.listen(2)

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
 

    
    #not needed.calling accept() means handshake already succeeded
    #wait for the TCP handshake with a client to complete
    #readable, _, _ = select.select([conn_sock], [],[], 5)


def connect_receive_and_process_data_from_client():
    while True:
       # wait for data to arrive from the network (watch the list of Readable sockets )
       readable, _, _ = select.select([listening_socket]+ list(clients.keys()),[],[])
       
       for sock in readable:
           if sock is listening_socket:
             listening_socket.setblocking(False)
               #we have a new connection
             connx, addr = listening_socket.accept()
             connx.setblocking(False)
             clients[connx] = b""

           else:
               #i.e we have an existing connection from a client
             data = sock.recv(1024)
             
             if not data:
                 #client disconnected
                sock.close()
                del clients[sock]
                continue
                    
             clients[sock] += data 
             
             while True:
                print('executing the resp parser now') 
                try:
                   resp_args, leftover = resp_parser(clients[sock])
                   print(resp_args)
                   clients[sock] = leftover
                
                #call resp executor
                   value_to_send = execute_commands.execute_commands(resp_args)
                   sock.sendall(value_to_send)
            
                except ValueError:
                  print(f"parsing Error")
                  break

try:
    connect_receive_and_process_data_from_client()

except KeyboardInterrupt:
    print("\nShutting down server")

finally:
    listening_socket.close()
    for sock in list(clients.keys()):
        sock.close()
