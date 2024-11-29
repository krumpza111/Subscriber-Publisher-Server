from socket import * 
import threading 
import time
from msgQueue import msgQueue, Node

HOST = '127.0.0.1'
PORT = 4080

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

                # if not subscribed check if publisher is subscribed to another topic
                # if so send an error message back, or subscribe to topic
                if user_name not in subscribers[topic]:
                    prev_subbed = False
                    for t in topics:
                        if user_name in subscribers[t]:
                            prev_subbed = True
                            break 
                    if prev_subbed:
                        response = '<ERROR: Not Subscribed>' 
                        connectionSocket.send(response.encode())
                    else:
                        subscribers[topic][user_name] = connectionSocket

                # Begin publisher operations 
                # Forward data to subscribers who are online 
                if topic not in topics:
                    response = '<ERROR: Subject not found>'
                    connectionSocket.send(response.encode()) 
                else:
                    queues[topic].enqueue(message)
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
                if topic in subscribers:
                    #adding client name to subscriber list 
                    if connectionSocket not in subscribers[topic]:
                        subscribers[topic][user_name] = connectionSocket
                    response = '<SUB_ACK>'
                    connectionSocket.send(response.encode())
                    while True:
                        # Forward all messages out to the subscriber
                        try:
                            try:
                                request = connectionSocket.recv(64).decode()
                                if request == '<DISC>':
                                    break
                            except Exception as e:
                                print(f"Error receiving data: {e}")
                            if queues[topic].size == 0:
                                response = "Queue is empty"
                                connectionSocket.send(response.encode())
                            message = queues[topic].dequeue()
                            if message:
                                connectionSocket.send(message.encode())
                        except Exception as e:
                            print(f"Error while dequeing message: {e}")
                            break
            except socket.timeout:
                print(f"Timedout waiting for data, closing connection") 
                break
    except IOError:
        print("IO Error")
        connectionSocket.close()
    return 

def handle_connection(connectionSocket, user_name):
    if user_name in active_clients:
        old_connection, old_thread = active_clients[user_name]
        return old_connection
    else:
        active_clients[user_name] = (connectionSocket, None)
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
            else:
                print("Invalid thread type ")
                break 
            num_threads += 1 
            thread.start()
            active_clients[user_name] = (connectionSocket, thread)
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

