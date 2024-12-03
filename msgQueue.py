import threading
from threading import Lock

MSG_LIMIT = 10

'''
Object representing a message block within the queue
@param message -- message being contained in node 
'''
class Node:
    def __init__(self, message):
        self.message = message
        self.next = None 

    def __str__(self):
        return f"{self.message}" 
    
'''
Object representing a linked list messaging queue with a FIFO structure 
    @param size -- Number of messages in the array 
    @param topic -- topic which the message queue is holding messages for 
    @param index_map -- Holds mappings of user_name with held index
    @param producers -- The producers which are adding messages to this thread
    @param lock -- Thread mutex lock 
    @param queue_full -- Condition variable signaling the queue is full 
    @param queue_empty -- Condition variable signaling the queue is empty
'''
class msgQueue:
    def __init__(self, topic):
        self.head = None
        self.size = 0
        self.topic = topic
        self.index_map = {} # Format {user_name : last_index_seen }
        self.producers = []
        self.lock = Lock() 
        self.queue_full = threading.Condition(self.lock) 
        self.queue_empty = threading.Condition(self.lock)

    '''
    Thread-safe enqueuing will add a message to the queue unless the queue is full 
    '''
    def enqueue(self, msg):
        with self.lock:
            # if queue if full need to wait for free space
            if self.size >= MSG_LIMIT:
                print("queue exceeds message size")
                self.queue_full.wait() 
            new_node = Node(msg)
            # If queue empty the head is the new node
            if self.head == None:
                self.head = new_node
                new_node.next = None 
                self.size = 1
            # Otherwise add to end of the queue
            else:
                curr_node = self.head 
                while (curr_node.next != None):
                    curr_node = curr_node.next 
                curr_node.next = new_node 
                new_node.next = None
                self.size += 1
            self.queue_empty.notify()

    '''
    Thread-safe dequeuing will the head (FIFO) from the queue and return the message 
    back to the client
    '''
    def dequeue(self):
        with self.lock:
            # If queue is empty need to wait for items to be added
            if self.size == 0:
                self.queue_empty.wait() 

            new_head = self.head.next 
            old_head = self.head 
            self.head = new_head 
            self.size -= 1 
            self.queue_full.notify_all() 
        return old_head.message
    
    '''
    Thread-safe method, simaler to deqeuing. Removes all messages not yet received by 
    this specific user. Does dequeuing multiple times.
    '''
    def get_messages(self, user_name):
        with self.lock:
            if user_name not in self.index_map:
                print("Error: Permission Denied") 
                return None

            # If queue is empty need to wait for items to be added
            if self.size == 0:
                self.queue_empty.wait()

            # Takes all messages starting from the index in the queue's index_map 
            # Adds them to new_messages and increases the index
            start_index = self.index_map[user_name] 
            new_messages = []
            curr_node = self.head 
            curr_index = 0 
            while curr_node:
                if curr_index >= start_index:
                    new_messages.append(curr_node.message) 
                curr_node = curr_node.next 
                curr_index += 1

            self.index_map[user_name] = self.size
        return new_messages
            
      


