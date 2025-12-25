import random

class Robot:
    def __init__(self, id):
        self.id = id
        self.failed = False
        self.death_handled = False # Flag for OS task migration
        self.shared_counter = 0    # Common resource data
        self.in_cs = False         # Critical Section flag
        self.x = random.randint(0, 9)
        self.y = random.randint(0, 9)

    def move(self, all_robots=None):
        """Simple movement logic with collision detection."""
        if self.failed:
            return

        for _ in range(15): # Try up to 15 times to find a free spot
            dx, dy = random.choice([-1, 0, 1]), random.choice([-1, 0, 1])
            nx, ny = max(0, min(9, self.x + dx)), max(0, min(9, self.y + dy))

            collision = False
            if all_robots:
                for r in all_robots:
                    if r.id != self.id and r.x == nx and r.y == ny:
                        collision = True
                        break
            
            if not collision:
                self.x, self.y = nx, ny
                return

def robot_task(robot, mq, mutex, idx, all_robots):
    """The main process loop for each robot."""
    print(f"[SYSTEM] Robot {robot.id} started.")
    
    while not robot.failed:
        # 1. Random Failure Simulation (chance per tick)
        if random.random() < 0.01: 
            robot.failed = True
            robot.in_cs = False
            print(f"!!! [FAIL] Robot {robot.id} has CRASHED !!!")
            return 

        # 2. Robot Action: Movement
        robot.move(all_robots)

        # 3. Critical Section: Mutual Exclusion (Mutex)
        if not robot.in_cs:
            if mutex.request(robot.id, all_robots):
                robot.in_cs = True
                print(f"[CS] Robot {robot.id} ENTERED Critical Section.")
                # Simulate work inside Critical Section for 5 scheduler cycles
                for _ in range(5):
                    if robot.failed: break 
                    yield 
                
                # Modify shared data safely
                robot.shared_counter += 1
                mutex.release(robot.id)
                robot.in_cs = False
                print(f"[CS] Robot {robot.id} EXITED Critical Section.")

        # 4. IPC: Messaging (Optimized logs)
        if random.random() < 0.2:
            alive_targets = [r.id for r in all_robots if not r.failed and r.id != robot.id]
            if alive_targets:
                target = random.choice(alive_targets)
                buf_status = mq.send(robot.id, target, f"Data {robot.id}")
                if buf_status:
                    print(f"[MSG] {robot.id} -> {target} | Receiver Buffer: {buf_status}")

        # 5. Receive messages from buffer
        msg = mq.receive(robot.id)
        if msg:
            rem = len(mq.queues[robot.id])
            print(f"[MSG] {robot.id} RECEIVED '{msg}' | Buffer left: {rem}/{mq.buffer_limit}")

        # Cooperative multitasking: give control back to the scheduler
        yield