import threading
from threading import Lock

MSG_LIMIT = 10

class Node:
    def __init__(self, message, next):
        self.message = message
        self.next = next 

    def __str__(self):
        return f"{self.message}" 
    
class msgQueue:
    def __init__(self, topic):
        self.head = None
        self.size = 0
        self.topic = topic
        self.lock = Lock() 
        self.queue_full = threading.Condition(self.lock) 
        self.queue_empty = threading.Condition(self.lock)

    def enqueue(self, msg):
        with self.lock:
            if self.size >= MSG_LIMIT:
                self.queue_full.wait() 
            new_node = Node(msg, None)
            if self.head == None:
                self.head = new_node
                new_node.next = None 
                self.size = 1
            else:
                curr_node = self.head 
                while (curr_node.next != None):
                    curr_node = curr_node.next 
                curr_node.next = new_node 
                curr_node.next.next = None
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
            self.queue_full.notify() 
        return old_head.message
      


