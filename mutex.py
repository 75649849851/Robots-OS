class Mutex:
    def __init__(self):
        self.lock_owner = None
        self.queue = [] # Robots waiting for the resource

    def _cleanup_dead_robots(self, all_robots):
        """Internal safety check: remove crashed robots from the lock system."""
        # 1. If the robot holding the lock died, release it immediately
        if self.lock_owner is not None:
            owner_robot = next((r for r in all_robots if r.id == self.lock_owner), None)
            if owner_robot and owner_robot.failed:
                print(f"[MUTEX] Owner Robot {self.lock_owner} died! Force releasing lock.")
                self.lock_owner = None

        # 2. Remove dead robots from the waiting list to prevent deadlocks
        alive_ids = set(r.id for r in all_robots if not r.failed)
        for q_id in self.queue:
            if q_id not in alive_ids:
                print(f"[MUTEX] Removing dead Robot {q_id} from waiting queue.")
        
        self.queue = [uid for uid in self.queue if uid in alive_ids]

    def request(self, robot_id, all_robots):
        """Attempt to enter the Critical Section."""
        self._cleanup_dead_robots(all_robots)

        # Success if already owner
        if self.lock_owner == robot_id:
            return True
            
        # Success if lock is free and it's this robot's turn
        if self.lock_owner is None:
            if not self.queue or self.queue[0] == robot_id:
                self.lock_owner = robot_id
                if self.queue and self.queue[0] == robot_id:
                    self.queue.pop(0)
                return True
        
        # If resource is busy, join the waiting queue
        if robot_id not in self.queue:
            self.queue.append(robot_id)
            
        return False

    def release(self, robot_id):
        """Exit Critical Section and make resource available for others."""
        if self.lock_owner == robot_id:
            self.lock_owner = None