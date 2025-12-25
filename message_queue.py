class MessageQueue:
    def __init__(self, buffer_limit=5):
        self.queues = {}
        self.last_message = None
        # Memory Management: limit how many messages a robot can store
        self.buffer_limit = buffer_limit 

    def register(self, robot_id):
        """Create a private mailbox for a robot."""
        self.queues[robot_id] = []

    def send(self, from_id, to_id, message):
        """Inter-Process Communication (IPC): Send a message if buffer is not full."""
        if len(self.queues[to_id]) < self.buffer_limit:
            self.queues[to_id].append(message)
            self.last_message = (from_id, to_id, message)
            # Return current buffer usage for logging
            return f"{len(self.queues[to_id])}/{self.buffer_limit}"
        else:
            # Flow Control: Reject message if memory is full
            print(f"[BUFFER OVERFLOW] Robot {to_id} rejected msg from {from_id}!")
            return None

    def receive(self, robot_id):
        """Retrieve the oldest message from the buffer (FIFO)."""
        if self.queues[robot_id]:
            return self.queues[robot_id].pop(0)
        return None