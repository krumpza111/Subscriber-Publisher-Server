from socket import * 
import threading 
import time
from msgQueue import msgQueue, Node

HOST = '127.0.0.1'
PORT = 4082

num_threads = 0

subscribers = {'WEATHER': {}, 'NEWS': {}} 
topics = ['WEATHER', 'NEWS']
messages = {'WEATHER': [], 'NEWS' : []}
active_clients = {} # Format {'user_name': (ConnectionSocket, thread)}

queues = {}
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

                #If a disconnect is received 
                if token_arr[0] == 'DISC':
                    response = '<DISC_ACK>' 
                    connectionSocket.send(response.encode()) 
                    break

                # request data we need
                topic = token_arr[2]
                message = token_arr[3]

                if topic not in topics:
                    response = '<ERROR: Subject not found>'
                    connectionSocket.send(response.encode()) 

                # if not subscribed check if publisher is subscribed to another topic
                # if so send an error message back, or subscribe to topic
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
                        queues[topic].producers.append(user_name)

                # Begin publisher operations 
                # Forward data to subscribers who are online 
                queues[topic].enqueue(message)
                for user in active_clients:
                    print("Client is: " + user) 
                    if user in queues[topic].index_map:
                        queues[topic].index_map[user] += 1
                        connection = active_clients[user] 
                        connection.send(message.encode())
                        
                print("Messages published and forwarded")
            except socket.timeout:
                print("Request message was empty") 
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
            #Accept requests from the client
            try:
                request = connectionSocket.recv(1024).decode()

                #Break down request and tokenize it
                request_str = request.strip('<>')
                print("Request message: " + request_str)
                token_arr = [x.strip() for x in request_str.split(',')] 

                #If a disconnect is received 
                if token_arr[0] == 'DISC':
                    response = '<DISC_ACK>' 
                    connectionSocket.send(response.encode()) 
                    break

                # request data we need
                topic = token_arr[2]

                # Begin consumer operations 
                # Subscribe to a topic and consume data from message queue
                if topic in topics:
                    #adding client name to subscriber list 
                    if user_name not in queues[topic].index_map:
                        queues[topic].index_map[user_name] = 0
                    response = '<SUB_ACK>'
                    connectionSocket.send(response.encode())
                    while True:
                        # Get all missed messages out to the subscriber
                        messages = queues[topic].get_messages(user_name) 
                        if messages:
                            print("Sending messages now")
                            for msg in messages:
                                try:
                                    connectionSocket.send(msg.encode())
                                except Exception as e:
                                    print(f"Error sending message to {user_name}: {e}")
                                    break
                            break
                        else:
                            print("No new messages")
                else:
                    # maybe return an error statement instead
                    print("Not a valid topic to subscribe to")
            except socket.timeout:
                print(f"Timedout waiting for data, closing connection") 
                break
    except IOError:
        print("IO Error")
        connectionSocket.close()
    return 

def handle_connection(connectionSocket, user_name):
    if user_name in active_clients:
        old_connection = active_clients[user_name]
        return old_connection
    else:
        return connectionSocket

def main():
    global num_threads
    serverSocket = socket(AF_INET, SOCK_STREAM) 
    serverSocket.bind((HOST, PORT)) 
    serverSocket.listen() 
    print("Ready to connect... ") 
    
    while True:
        try:
            connectionSocket, addr = serverSocket.accept() 
            print("Connected ... ")
            request = connectionSocket.recv(1024).decode().strip('<>')
            print("Request message: " + request)
            token_arr = [x.strip() for x in request.split(',')] 
            if token_arr[1] == "CONN":
                connectionSocket.send("<CONN_ACK>".encode())
            elif token_arr[1] == "RECONNECT":
                connectionSocket.send("<RECONNECT_ACK>".encode())
            user_name = token_arr[0]
            if user_name in active_clients.keys():
                response = "Error: user is already connected, choose another user name"
                connectionSocket.send(response.encode())

            thread_type = user_name.split(maxsplit=1)[0]
            connectionSocket = handle_connection(connectionSocket, user_name)
            #connectionSocket.settimeout(180) # 3 minute timeout
            if thread_type == "Publisher" or thread_type == "Pub":
                thread = threading.Thread(target=producer_thread_func, args=(connectionSocket, user_name, ))
            elif thread_type == "Subscriber" or thread_type == "Sub":
                thread = threading.Thread(target=consumer_thread_func, args=(connectionSocket, user_name, ))
                active_clients[user_name] = connectionSocket
            else:
                print("Invalid thread type ")
                break 
            num_threads += 1 
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
    main() 

