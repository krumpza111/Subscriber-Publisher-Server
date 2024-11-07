# Subscriber-Publisher-Server
A server which displays published messages to all users subscribed 

Server-Side Implementation:
* Always On * 
- Listens for incoming connections from various clients simultaneously (done with threading)
- Tokenize the request string from the client to figure what action they want to take
- Manages subscribed clients and published messages using a dictionary and array 
- Handles publishing and subscriber requests by forwarding data, or adding users to a subscription
- Maintains thread until a specific user wants to disconnect 
  
Client-Side Implementation:
Subscribers -> Need to subscribe to one subject before receiving messages 
Publishers -> Publishes messages to the subject indicated to the server
- Client is prompted to register a name and send it to the server
- Clients establish a connection with the server (notified by a CONN_ACK token) 
- The clientis prompted to send instructions to the server and gets server responses back
- There is a select.select() method being used which is simaler to poll() in C ...
(continued) It checks if data is available to read from the socket or if there is data being sent in standard input
- The client can end the connection at any time using a DISC token and will receive a DISC_ACK back to ensure socket is closed

There are two predefined subject: WEATHER and the NEWS 

Operation | Client Message  | Server Response

===============================================
CONNECT     <NAME, CONN>       <CONN_ACK> 
SUBSCRIBE  <CLIENT_NAME, SUB,  <SUB_ACK> 
            SUBJECT>      
PUBLISH    <CLIENT_NAME, PUB,  (Forwards message to subscribers) 
            SUBJECT, MSG>      OR ERROR
DISCONNECT  <DISC>             <DISC_ACK
