class Node:
    def __init__(self, message, next):
        self.message = message
        self.next = next 

    def __str__(self):
        return f"{self.message}" 