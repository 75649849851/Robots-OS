# Robot OS

## Description
Imitation of operating system with 6 robots.

## How to run
Run python file main.py


##Logic of each code component

1. main.py (The Kernel & Fault Tolerance Manager)
This is the heart of the simulation. It acts as the Operating System Kernel.

Initialization: It creates the shared resources (Message Queue, Mutex, Scheduler) and the hardware entities (Robots).

The Main Loop: It drives the clock. Every "tick," it calls the scheduler to execute a small piece of code from one robot.

Fault Tolerance Logic: This is the most important part of main.py. It constantly monitors the "health" of robots. If a robot's failed flag becomes True, the kernel:

Calculates the distance to all alive robots.

Identifies the nearest survivor.

Migrates the task: It moves the shared_counter (the "work") from the dead robot to the survivor.

Sends a system message via IPC to notify the survivor of the inheritance.


2. robot.py (Process Logic & Tasks)
This file defines what a "process" does in this OS.

The Robot Class: Represents the state of the process (location, data, health, and whether it is currently in a Critical Section).

The robot_task (Generator): This is a coroutine. Instead of running a while True loop that blocks the whole computer, it uses yield.

Each yield tells the OS: "I have done a little bit of work; you can let someone else use the CPU now."

It handles the logic of requesting the Mutex, doing work (incrementing a counter), and sending random messages to peers.


3. scheduler.py (CPU Management)
This implements a Round Robin Scheduler using a "Ready Queue."

ready_queue: A deque (double-ended queue) that holds all active robot tasks.

run_one(): 1. It pulls the task from the front of the queue. 2. It executes it until the next yield (using next(task)). 3. If the task is not finished, it puts it back at the end of the queue. This ensures that no single robot "hogs" the CPU and everyone gets a fair share of execution time.


4. mutex.py (Synchronization & Deadlock Prevention)
This file manages access to shared resources.

The Lock System: It ensures only one robot can have lock_owner == robot_id at a time.

The Wait Queue: If Robot A has the lock and Robot B requests it, Robot B is placed in a queue.

Deadlock Recovery: A unique feature here is _cleanup_dead_robots. In a real OS, if a process dies while holding a Mutex, the whole system might freeze (Deadlock). This code detects if the lock_owner has crashed and force-releases the lock so other robots can continue.


5. message_queue.py (Inter-Process Communication - IPC)
This simulates how processes send data packets to each other.

Mailboxes: Each robot has its own list (queue) inside the queues dictionary.

Flow Control (Buffer Limit): The buffer_limit=3 is a critical OS concept. If a robot is busy and doesn't read its messages, its "mailbox" fills up. Once it reaches 3, any new incoming messages are dropped (Buffer Overflow), simulating memory constraints in a real system.

FIFO: It uses First-In-First-Out logic to ensure messages are read in the order they were sent.


6. visualizer.py (System Monitor)
This is the GUI/Dashboard of the Operating System.

State Visualization: It maps the internal variables to colors:

Green: Process is running normally.

Yellow: Process is in the Critical Section (holding the Mutex).

Red: Process has crashed (Hardware/Software Failure).

Link Visualization: It draws Blue lines for IPC messages and Purple lines for Task Migration (Fault Tolerance), allowing you to see the "invisible" OS operations.

The Ready Queue Monitor: On the right side, it shows exactly which tasks are waiting in the Scheduler's queue.


##Summary of Interaction
When you run the code:

1.	main.py starts.
2.	scheduler.py gives 1 "tick" of time to a robot_task.
3.	The robot_task asks mutex.py for permission to update data.
4.	The robot_task sends a message through message_queue.py.
5.	visualizer.py draws these events on your screen.
