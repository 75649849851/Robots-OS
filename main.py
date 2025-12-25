import pygame
import sys
import math 
from robot import Robot, robot_task
from scheduler import Scheduler
from message_queue import MessageQueue
from mutex import Mutex
from visualizer import Visualizer

def main():
    num_robots = 6
    # Initialize components
    robots = [Robot(i) for i in range(num_robots)]
    # Buffer Management: Limit of 3 messages to demonstrate overflow clearly
    mq = MessageQueue(buffer_limit=3) 
    scheduler = Scheduler()
    mutex = Mutex()

    # Register each robot in the messaging system
    for r in robots:
        mq.register(r.id)

    # Create and add tasks (processes) for the scheduler
    for i, r in enumerate(robots):
        task = robot_task(r, mq, mutex, i, robots)
        scheduler.add_task(task)

    vis = Visualizer(robots, scheduler, mq)
    clock = pygame.time.Clock()

    running = True
    while running:
        # Control simulation speed (5 Frames Per Second)
        clock.tick(5) 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- FAULT TOLERANCE LOGIC: Task Migration & Replication ---
        dead_robots = [r for r in robots if r.failed and not r.death_handled]
        alive_robots = [r for r in robots if not r.failed]

        for dead_r in dead_robots:
            if alive_robots:
                # Find the CLOSEST alive robot to take over the work
                target = min(alive_robots, key=lambda n: math.hypot(n.x - dead_r.x, n.y - dead_r.y))
                
                dead_r.death_handled = True
                
                # Replication: Transfer data from the dead robot to the survivor
                target.shared_counter += dead_r.shared_counter
                
                # Visual effect for migration
                vis.add_migration(dead_r.id, target.id)
                print(f"[MIGRATION] Robot {dead_r.id} DIED. Data {dead_r.shared_counter} moved to Robot {target.id}!")
                
                # System notification to the new task owner
                mq.send(999, target.id, f"SYSTEM: Task inherited")
            else:
                if not any(not r.failed for r in robots):
                    print(f"[CRITICAL] All robots are dead. Simulation halted.")
                dead_r.death_handled = True

        # --- SCHEDULING ---
        # Execute one step of the current process in the queue
        scheduler.run_one()
        
        # --- GRAPHICS ---
        vis.draw()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()