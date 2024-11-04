# Subscriber-Publisher-Server
A server which displays published messages to all users subscribed 

Server-Side Implementation:
- Listens for incoming connections from various clients simultaneously (done with threading)
- Manages client subscriptions
- Handles publishing and subscriber requests
- Distributes messages to subscribers
  
Client-Side Implementation:
Subscribers -> Need to subscribe to one subject before receiving messages 
Publishers -> Publishes messages to the subject indicated to the server

There are two predefined subject: WEATHER and the NEWS 

Operation | Client Message  | Server Response
===============================================
CONNECT     <NAME, CONN>       <CONN_ACK> 
SUBSCRIBE  <CLIENT_NAME, SUB,  <SUB_ACK> 
            SUBJECT>      
PUBLISH    <CLIENT_NAME, PUB,  (Forwards message to subscribers) 
            SUBJECT, MSG>      OR ERROR
DISCONNECT  <DISC>             <DISC_ACK
