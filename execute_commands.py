#The primary data store for the redis server instance. A basic dictionary.
#Redis is basically a key-value store. everything in redis is stored under a key.
#
my_primary_store = {b'Game Top Score': b'1500', b'Top scorer': b'Ade'}

def execute_commands(args) -> bytes:
    '''
    params:
     args is a list of byte strings holding a complete RESP frame arguments received from a client
     This function will try to execute the RESP command sent if any exists in the received RESP frame
     args has this format= [ b'<arg0: a valid redis command e.g. GET'>, b'arg1', b'arg2'...]
    '''
    print("The 'execute command' function is called")
    
    if not args:
        return b"Empty command\r\n"
    command_to_execute = args[0].upper() #the first argument in the list is the command to be executed, followed by parameters for that command 
    if command_to_execute == b'PING':
        return b"+PONG\r\n"
    
    elif command_to_execute == b'ECHO':  #echo command sent with REDIS protocol must always have one argument#
        if len(args) != 2:
            return b"-ERR Too many arguments. Please specify only one argument for the echo command"
        return b"$%d\r\n%s\r\n" % (len(args[1]), args[1]) 
    
    elif command_to_execute == b'SET': 
        #FOR DEBUGGING: TO REMOVE
        print("The dictionary storing the redis server data:", my_primary_store)
        #for a valid RESP string, we expect two arguments for a Redis SET command: 
        # a key and a value(Plus SET command itself means expected length of args is 3)
        if len(args) != 3:
            return b"-ERR invalid argument list\r\n"
        
        my_primary_store[args[1]] = args[2]  
        #FOR DEBUGGING: TO REMOVE
        print("The dictionary storing the redis server data after SET command:", my_primary_store)
        return b"+OK\r\n"
            
        
    elif command_to_execute == b'GET':
        #will return the value for the key specified in the GET command received
        # for a valid RESP string we expect one argument for a Redis GET command
        #the key of the value we want to get(plus the GET command itself means expected length of args is 2)
        if len(args) == 2:
            print("The dictionary storing the redis server data:", my_primary_store)
            print
            if my_primary_store.get(args[1])!= None:
               return my_primary_store[args[1]]
            else:
                return b"The key specified does not exist\r\n"
        else:
          return b"-Err, Invalid argument count! please specify only the GET Command and one key to get\r\n"
      
    elif command_to_execute == b'DEL':
        ''' will delete the value(s) for the key(s) passed as argument to the DEL command
            and return the number of keys removed
        '''            
        deleted = 0
        if len(args) < 2:
            return  b'-ERR Wrong number of arguments. specify at least one key to delete in the redis store'
        for key in args[1:]:
            print("key is:", key)
            value_deleted = my_primary_store.pop(key, None)
            print("datastore is now:", my_primary_store)
            if value_deleted is not None:
                deleted += 1
        return b":%d\r\n" % deleted