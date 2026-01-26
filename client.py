import socket
import sys
import select
import errno

def send_message():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    with sock:
        try:
           sock.connect(('localhost', 6379))
        except BlockingIOError:
           #connection in progress
           pass
        
        #wait for the TCP handshake to complete
        _, writable, _ = select.select([],[sock],[],5) #select returns three lists: readable, writable and errored sockets
        
        if sock not in writable:
               raise TimeoutError("Server connection timeout. Seems no redis server is up")  
               
        else:  
           #the TCP handshake attempt has been completed, we can now work with the socket. 
           # First, we check if the NONBLOCKING connect we initiated succeeded
           err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
           if err != 0:
                raise OSError(err, errno.errorcode.get(err, "Unknown error"))  
            
           else:
               #err==0
               #connection successful
               #build RESP frame
            msg = (f"*2\r\n"
                  f"$3\r\n"
                  f"GET\r\n"
                  f"$14\r\n"
                  f"Game Top Score\r\n"
                  ).encode('utf-8')
            print("length of encoded string to send:",len(msg))
            
            #---- sending message --------
           
            msgbytes_sent_so_far = 0
            while msgbytes_sent_so_far < len(msg):
               _, write, _ = select.select([],[sock],[], 5)
               if not write:
                   raise TimeoutError("Server buffer is full. Send operation timed out")     
               
               try:
                byte_send = sock.send(msg[msgbytes_sent_so_far:]) #send message to the OS buffer, returns int value of number of bytes successfully queued to the os send buffer
                msgbytes_sent_so_far += byte_send 
               except BlockingIOError:
                 continue
              

         #----- receiving -------
           response = b""
           while True:
             # wait for data to arrive from the network (Readable)
              readable, _, _ = select.select([sock],[],[], 5)
              if not readable:
                 raise TimeoutError("Receive timeout: No data from Redis server")     
              try:
                 chunk = sock.recv(1024)
                 if not chunk:
                     break
                 response += chunk
                 
                 if is_resp_complete(response):
                     print("Response:", response.decode('utf-8'))
                     break
              except BlockingIOError:
                continue
            

def is_resp_complete(response):
    """
    Helper function to check if the RESP response is complete.
    For GET commands, the response is a bulk string:
    - If found: $<length>\r\n<data>\r\n
    - If not found: $-1\r\n
    """
    if not response:
        return False
    
    # Must end with \r\n for a complete RESP message
    if not response.endswith(b'\r\n'):
        return False
    
    # Check for null bulk string response
    if response == b'$-1\r\n':
        return True
    
    # Parse bulk string response
    if response.startswith(b'$'):
        try:
            # Find the first \r\n to get the length line
            first_crlf = response.find(b'\r\n')
            if first_crlf == -1:
                return False
            
            # Extract and parse the length
            length_str = response[1:first_crlf].decode('utf-8')
            length = int(length_str)
            
            # The data starts after the first \r\n
            data_start = first_crlf + 2
            expected_end = data_start + length + 2  # +2 for the trailing \r\n
            
            # Check if we have received all the expected bytes
            return len(response) >= expected_end
        except (ValueError, UnicodeDecodeError):
            return False
    
    return False


send_message()


