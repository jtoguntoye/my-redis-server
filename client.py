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
                   raise TimeoutError("Server buffer is full")     
               
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
                 
                 #--TODO implement check if response is complete(e.g ends with \r\n)
                 #This logic depends on the specific redis command result type.
                 # if is_resp_complete(response):
                 print("Response:", response.decode('utf-8'))
                 break
              except BlockingIOError:
                continue
            

send_message()

#--TODO ---
#def is_resp_complete(response):
#Helper function to check if the response received is complete depending on the type of redis command sent


