import threading
from threading import Lock

MSG_LIMIT = 10

class Node:
    def __init__(self, message):
        self.message = message
        self.next = None 

    def __str__(self):
        return f"{self.message}" 
    
class msgQueue:
    def __init__(self, topic):
        self.head = None
        self.size = 0
        self.topic = topic
        self.index_map = {} 
        self.producers = []
        self.lock = Lock() 
        self.queue_full = threading.Condition(self.lock) 
        self.queue_empty = threading.Condition(self.lock)

    def enqueue(self, msg):
        with self.lock:
            if self.size >= MSG_LIMIT:
                print("queue exceeds message size")
                self.queue_full.wait() 
            new_node = Node(msg)
            if self.head == None:
                self.head = new_node
                new_node.next = None 
                self.size = 1
            else:
                curr_node = self.head 
                while (curr_node.next != None):
                    curr_node = curr_node.next 
                curr_node.next = new_node 
                new_node.next = None
                self.size += 1
            self.queue_empty.notify()

    def dequeue(self):
        with self.lock:
            if self.size == 0:
                self.queue_empty.wait() 

            new_head = self.head.next 
            old_head = self.head 
            self.head = new_head 
            self.size -= 1 
            self.queue_full.notify_all() 
        return old_head.message
    
    def get_messages(self, user_name):
        with self.lock:
            if user_name not in self.index_map:
                self.index_map[user_name] = 0 

            if self.size == 0:
                self.queue_empty.wait()

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
            
      


