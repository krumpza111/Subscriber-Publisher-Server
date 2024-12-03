from socket import * 
import threading 
import sys
from msgQueue import msgQueue

# Globals
HOST = '127.0.0.1'
PORT = 4084 # default port number being used

# Data storage
topics = ['WEATHER', 'NEWS'] # Topics available to subscribe & publish 
active_clients = {} # Format {'user_name': connectionSocket}
queues = {} # Format {'topic': queue for topic 't }

# Creates a message queue for each topic available
for t in topics:
    queues[t] = msgQueue(t)
    
'''
Producer thread function responsible for producing data and putting it into the 
message queue. this function is designated for publishers on the server
'''
def producer_thread_func(connectionSocket, user_name):
    try:
        while True:
            try:
                #Accept requests from the client
                request = connectionSocket.recv(1024)
                #Break down request and tokenize it
                request_str = request.decode().strip('<>')
                print("Request message: " + request_str)
                token_arr = [x.strip() for x in request_str.split(',')] 

                #If a disconnect is received send response and break from loop
                if token_arr[0] == 'DISC':
                    response = '<DISC_ACK>' 
                    connectionSocket.send(response.encode()) 
                    break

                # request data we need to process
                topic = token_arr[1]
                message = token_arr[2]

                if topic not in topics:
                    response = '<ERROR: Subject not found>'
                    connectionSocket.send(response.encode()) 

                # if not subscribed check if publisher is subscribed to another topic
                # if yes then send an error back
                if user_name not in queues[topic].index_map:
                    prev_subbed = False
                    for t in topics:
                        if user_name in queues[t].producers and t != topic:
                            prev_subbed = True
                            break 
                    if prev_subbed:
                        response = '<ERROR: Not Subscribed>' 
                        connectionSocket.send(response.encode())
                    else:
                        # Adds producer to this topics message queue
                        queues[topic].producers.append(user_name)

                # Begin publisher operations 
                # Add message to the queue
                queues[topic].enqueue(message)

                # Forward data to subscribers who are online 
                for user in active_clients:
                    if user in queues[topic].index_map:
                        queues[topic].index_map[user] += 1
                        connection = active_clients[user] 
                        connection.send(message.encode())
                        
                print("Messages published and forwarded")
            except Exception as e:
                print(f"Error: {e}")
                break
    except IOError:
        print("IO Error")
        connectionSocket.close()
    return 

'''
Consumer thread function responsible for consuming data from the message queue
these threads are designated to those who are subscribers on the server
'''
def consumer_thread_func(connectionSocket, user_name):
    try:
        while True:
            #Accepting requests from the client
            try:
                # Get any missed messages out to the subscriber
                for topic in topics:
                    if user_name in queues[topic].index_map:
                        messages = queues[topic].get_messages(user_name) 
                        if messages is None:
                            break
                        if messages:
                            #Sending messages out 
                            for msg in messages:
                                try:
                                    connectionSocket.send(msg.encode())
                                except Exception as e:
                                    print(f"Error sending message to {user_name}: {e}")
                                    break

                # Receive request from client
                request = connectionSocket.recv(1024).decode()
                if request is None:
                    continue

                #Break down request and tokenize it
                request_str = request.strip('<>')
                print("Request message: " + request_str)
                token_arr = [x.strip() for x in request_str.split(',')] 

                #If a disconnect is received, remove the user from active clients and exit loop
                if token_arr[0] == 'DISC':
                    response = '<DISC_ACK>' 
                    connectionSocket.send(response.encode()) 
                    del active_clients[user_name]
                    break

                # request data we need
                topic = token_arr[2]

                # Begin consumer operations 
                # Subscribe to a topic and consume data from message queue
                if topic in topics:
                    #adding client name to subscriber list 
                    if user_name not in queues[topic].index_map.keys():
                        queues[topic].index_map[user_name] = 0
                    response = '<SUB_ACK>'
                    connectionSocket.send(response.encode())
                    continue
                else:
                    # maybe return an error statement instead
                    response = "ERROR: Subscription Failed - Subject Not Found"
                    connectionSocket.send(response.encode())
                    continue
            
            except Exception as e:
                print(f"Error seen now: {e}")
                break
    except IOError:
        print("IO Error")
        connectionSocket.close()
    return 

'''
Main server loop:
1. Handles accepting client connections, and sending ACK responses
2. Adds user to the active clients list
3. Creates thread based on if the client is a publisher or subscriber
- Can exit using SIGINT
'''
def main():
    # Setting up and listening on port
    serverSocket = socket(AF_INET, SOCK_STREAM) 
    serverSocket.bind((HOST, PORT)) 
    serverSocket.listen() 
    print(f"Ready to connect on port {PORT}... ") 
    
    while True:
        try:
            # main accept loop
            connectionSocket, addr = serverSocket.accept() 
            print("Connected ... ")

            request = connectionSocket.recv(1024).decode().strip('<>')
            print("Request message: " + request)

            # Split the request into tokens
            token_arr = [x.strip() for x in request.split(',')] 
            user_name = token_arr[0]

            # Process connection and reconnection of user
            if token_arr[1] == "CONN":
                connectionSocket.send("<CONN_ACK>".encode())
                if user_name in active_clients.keys():
                    response = "Error: user is already connected, choose another user name"
                    connectionSocket.send(response.encode())
            elif token_arr[1] == "RECONNECT":
                connectionSocket.send("<RECONNECT_ACK>".encode())

            # Determines if users are producers or consumers
            thread_type = user_name.split(maxsplit=1)[0]
            thread_type = thread_type.lower()
            if thread_type == "publisher" or thread_type == "pub":
                thread = threading.Thread(target=producer_thread_func, args=(connectionSocket, user_name, ))
            elif thread_type == "subscriber" or thread_type == "sub":
                active_clients[user_name] = connectionSocket
                thread = threading.Thread(target=consumer_thread_func, args=(connectionSocket, user_name, ))
            else:
                print("Invalid thread type ")
                break 
            thread.start()

        except KeyboardInterrupt:
            print("\n Shutting down server now... ") 
            break
        except Exception as e:
            print(f"Error in main thread: {e}")
            break
    
    serverSocket.close()
    print("Goodbye")

if __name__ == "__main__":
    # Check for command line PORT argument
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1]) 
            if PORT < 1 or PORT > 65535:
                raise ValueError("Port number is outside of allowable range")
        except ValueError as e:
            print(f"Invalid port number: {e}")
            sys.exit(1)
    else:
        PORT = 4084
    main() 

