from socket import * 
import select
import sys

serverName = '127.0.0.1' 
serverPort = 4084
clientSocket = socket(AF_INET, SOCK_STREAM) 
clientSocket.connect((serverName, serverPort))

def main():
    try:
        while True:
            print("Ready for sending... ") 
            initial_msg = input("Please enter a command, or type help for more info \n")
            clientSocket.send(initial_msg.encode()) 
            data = clientSocket.recv(1024).decode() 
            if str(data) != '<CONN_ACK>' and str(data) != '<RECONNECT_ACK>':
                print("Error: Connection failed") 
                print(">> Server Response: " + str(data))
                clientSocket.close()
                return
            else:
                print(">> Server Response: " + str(data))
            while True:
                try:
                    print(">> ", end="")
                    # Simaler code to poll() in c (read list, write list, exceptionals list)
                    ready_to_read, _, _ = select.select([clientSocket, sys.stdin], [], [])
                    for source in ready_to_read:
                        if source == clientSocket:
                            try:
                                data = clientSocket.recv(1024).decode() 
                                if data == '<DISC_ACK>':
                                    break
                                elif data:
                                    print("Server Response: " + str(data))
                            except IOError:
                                print("IOErrror: receiving data from the server")
                        elif source == sys.stdin:
                            user_input = input()
                            token_arr = [x.strip() for x in user_input.split(',')] 
                            #print("Token array 1st token: " + token_arr[0])
                            if token_arr[0] == '<DISC>':
                                clientSocket.send(token_arr[0].encode()) 
                                data = clientSocket.recv(1024).decode() 
                                print("Server Response: " + str(data))
                                if data == '<DISC_ACK>':
                                    print("Disconnecting from server") 
                                    clientSocket.close()
                                    return
                                else:
                                    print("Error: Failed to disconnect") 
                                    continue
                            user_name = token_arr[0]
                            user_method = token_arr[1]
                            # Establish connection to server
                            if user_method == 'PUB':
                                # Publisher
                                outputdata = f'<{user_name}, {token_arr[1]}, {token_arr[2]}, {token_arr[3]}>'
                                clientSocket.send(outputdata.encode())
                            elif user_method == 'SUB':
                                # Subscriber 
                                outputdata = f'<{user_name}, {token_arr[1]}, {token_arr[2]}>' 
                                clientSocket.send(outputdata.encode()) 
                                data = clientSocket.recv(64).decode()
                                print("Server Response: " + str(data))
                                print()
                except Exception as e:
                    print(f"Error: {e}")
                    break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        clientSocket.close()
        print("Connection is closed")
                            

if __name__ == "__main__":
    main()