from socket import * 
import threading 

HOST = '127.0.0.1'
PORT = 6674

serverSocket = socket(AF_INET, SOCK_STREAM) 
serverSocket.bind((HOST, PORT)) 
serverSocket.listen() 
subscribers = {'WEATHER': {}, 'NEWS': {}} 
messages = {'WEATHER': [], 'NEWS' : []}

def thread_process(connectionSocket):
    currUser = None
    try:
        while True:
            request = connectionSocket.recv(1024) 
            if not request:
                print("Request message was empty") 
                break
            request_str = request.decode().strip('<>')
            token_arr = [x.strip() for x in request_str.split(',')] 
            if token_arr[0] == 'DISC':
                response = '<DISC_ACK>' 
                connectionSocket.send(response.encode()) 
                break
            user_method = token_arr[1]
            print(user_method) 
            if user_method == 'CONN':
                response = '<CONN_ACK>' 
                connectionSocket.send(response.encode())
                currUser = token_arr[0]

            elif user_method == 'SUB' and currUser == token_arr[0]:
                # Subscribers !!
                topic = token_arr[2]
                print(topic)
                if topic in subscribers:
                    print(topic)
                    # adding client name to subscriber list
                    subscribers[topic][currUser] = connectionSocket
                    response = '<SUB_ACK>' 
                    connectionSocket.send(response.encode())
                    # Gets cached messages
                    for msg in messages[topic]:
                        msg = msg + ' '
                        connectionSocket.send(msg.encode())
                else:
                    response = '<ERROR: Subscription Failed - Subject not found>'
                    connectionSocket.send(response.encode())

            elif user_method == 'PUB' and currUser == token_arr[0]:
                # Publishers !!
                topic = token_arr[2]
                message = token_arr[3]
                print(topic)
                if topic in subscribers:
                    messages[topic].append(message)
                    if subscribers[topic]:
                        print(subscribers[topic].values())
                        for subsciber in subscribers[topic].values():
                            print("forwarding message now")
                            subsciber.send(message.encode()) 
                    else:
                        response = '<ERROR: Subject not found>'
                        connectionSocket.send(response.encode())
                else:
                    response = '<ERROR: Not Subscribed>' 
                    connectionSocket.send(response.encode())
            else:
                # Was kicked most likely to not being a correct user name
                print("Error: Not Current User")
    except IOError:
        print("IO Error")
        connectionSocket.close()

print("Ready to connect... ") 
while True:
    connectionSocket, addr = serverSocket.accept() 
    thread = threading.Thread(target=thread_process, args = (connectionSocket, ))
    thread.start()

