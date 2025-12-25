from collections import deque

class Scheduler:
    def __init__(self):
        # The 'Ready Queue' holds all active processes
        self.ready_queue = deque()

    def add_task(self, task):
        """Add a new process to the end of the queue (FCFS/Round Robin style)."""
        self.ready_queue.append(task)

    def run_one(self):
        """Cooperative Multitasking: Run one step of the current process."""
        if not self.ready_queue:
            return
            
        # Pick the first task in line
        task = self.ready_queue.popleft()
        try:
            # Execute until the next 'yield'
            next(task)
            # If not finished, put it back at the end of the queue
            self.ready_queue.append(task)
        except StopIteration:
            # Task is completely finished
            pass