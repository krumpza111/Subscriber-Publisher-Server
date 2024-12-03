# Subscriber-Publisher-Server
A server which displays published messages to all users subscribed 
Usage: python3 server.py [PORT]
Usage: python3 client.py [PORT]

## Server-Side Application:
* Always On * 
- Listens for incoming connections from various clients simultaneously (done with a thread pool)
- Tokenize the request string from the client to figure what action(s) they want to take
- Handles publishing and subscriber clients by using seperate producer and consumer threads
- Maintains thread until a specific user wants to disconnect 

### Consumer Thread Implementation:
- Adds subscribers to the active_clients list
- Allows subscribers to subscribe to topics availble on the server 
- Subscribers receive all messages to topics they have subscribed to including unseen messages 
- Server maintains a record of the subscriber by tracking their user name and the last message from the queue received 
- Allows exit at any time using the disconnect token and maintains subscription 

### Producer Thrad Implementation:
- Allows publishers to add messages to the queue 
- Publishers forward messages immediately to any active clients 

## Client-Side Application:
Subscribers -> Need to subscribe to one subject before receiving messages 
Publishers -> Publishes messages to the subject indicated to the server
- If a port number is given the socket tries to connect to that port or uses port # 4084 as a default
- Client is prompted to register a name and send it to the server
- Clients establish a connection with the server (notified by a CONN_ACK token) 
- The clientis prompted to send instructions to the server and gets server responses back
- There is a select.select() method being used which is simaler to poll() in C that checks if data is available to read from the socket or if there is data being sent in standard input
- The client can end the connection at any time using a DISC token and will receive a DISC_ACK back to ensure socket is closed

There are two predefined subject: WEATHER and the NEWS 

## Message Format: 

| Operation | Client Message          | Server Response   |
| --------- | ----------------------  | ---------------   |
| CONNECT   |  <NAME, CONN>           | <CONN_ACK>        |
|           |                         |                   |
| SUBSCRIBE | <CLIENT_NAME, SUB,      |  <SUB_ACK>        |
|           |  SUBJECT>               |                   |
|           |                         |                   |
| RECONNECT | <RECONNECT, CLIENT_NAME>| <RECONNECT_ACK>   | 
|           |                         | + Queued messages |
|           |                         |                   |
| DISCONNECT|  <DISC>                 |<DISC_ACK> +       |
|           |                         |Subscription saved |
|           |                         |                   | 
| PUBLISH   | <PUB, SUBJECT, MSG>     | (Forward to active|
|           |                         | clients + queue if|
|           |                         | offline)          |
