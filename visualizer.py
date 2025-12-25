import pygame

# UI Configuration
CELL_SIZE = 60
GRID_SIZE = 10
SIDE_PANEL = 250
WINDOW_WIDTH = CELL_SIZE * GRID_SIZE + SIDE_PANEL
WINDOW_HEIGHT = CELL_SIZE * GRID_SIZE

# Colors
WHITE, GREEN, RED, YELLOW, BLACK, BLUE, PURPLE = (255,255,255), (0,200,0), (200,0,0), (255,255,0), (0,0,0), (0,0,255), (128,0,128)

class Visualizer:
    def __init__(self, robots, scheduler, mq):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Robot OS Simulation")
        self.robots, self.scheduler, self.mq = robots, scheduler, mq
        self.font = pygame.font.SysFont(None, 20)
        self.clock = pygame.time.Clock()
        self.active_messages = []
        self.active_migrations = []

    def add_migration(self, from_id, to_id):
        """Show a purple line when a task moves from a dead robot to a live one."""
        self.active_migrations.append((from_id, to_id, 8)) 

    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw Grid
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, (230,230,230), (0, i * CELL_SIZE), (600, i * CELL_SIZE))
            pygame.draw.line(self.screen, (230,230,230), (i * CELL_SIZE, 0), (i * CELL_SIZE, 600))

        # Draw Robots
        for r in self.robots:
            # Color reflects OS State: Running (Green), Critical Section (Yellow), Failed (Red)
            color = RED if r.failed else (YELLOW if r.in_cs else GREEN)
            cx, cy = int(r.x * CELL_SIZE + 30), int(r.y * CELL_SIZE + 30)
            pygame.draw.circle(self.screen, color, (cx, cy), 20)
            id_txt = self.font.render(str(r.id), True, BLACK)
            self.screen.blit(id_txt, id_txt.get_rect(center=(cx, cy)))

            # Buffer Status Text above robot
            current_load = len(self.mq.queues.get(r.id, []))
            buf_txt = self.font.render(f"Buf:{current_load}/{self.mq.buffer_limit}", True, (100,100,100))
            self.screen.blit(buf_txt, (cx - 25, cy - 40))

        # IPC Messaging Visualization (Blue lines)
        if self.mq.last_message:
            self.active_messages.append((*self.mq.last_message, 6))
            self.mq.last_message = None

        for msg in self.active_messages:
            if msg[0] < len(self.robots) and msg[1] < len(self.robots):
                r1, r2 = self.robots[msg[0]], self.robots[msg[1]]
                start, end = (r1.x*60+30, r1.y*60+30), (r2.x*60+30, r2.y*60+30)
                pygame.draw.line(self.screen, BLUE, start, end, 2)
                mid_x, mid_y = (start[0]+end[0])/2, (start[1]+end[1])/2
                txt = self.font.render("MSG", True, BLUE)
                self.screen.blit(txt, (mid_x, mid_y - 10))

        self.active_messages = [(a,b,t,f-1) for a,b,t,f in self.active_messages if f > 1]

        # Migration Visualization (Purple lines)
        for mig in self.active_migrations:
            r1, r2 = self.robots[mig[0]], self.robots[mig[1]]
            start, end = (r1.x*60+30, r1.y*60+30), (r2.x*60+30, r2.y*60+30)
            pygame.draw.line(self.screen, PURPLE, start, end, 4)
            mid_x, mid_y = (start[0]+end[0])/2, (start[1]+end[1])/2
            txt = self.font.render("TASK MIGRATION", True, PURPLE)
            self.screen.blit(txt, (mid_x, mid_y - 15))

        self.active_migrations = [(a,b,f-1) for a,b,f in self.active_migrations if f > 1]

        # --- SIDE PANEL: OS MONITOR ---
        px = 610
        self.screen.blit(self.font.render("OS MONITOR", True, BLACK), (px, 10))
        for i, r in enumerate(self.robots):
            status = "FAIL" if r.failed else ("CS" if r.in_cs else "OK")
            col = RED if r.failed else (YELLOW if r.in_cs else GREEN)
            txt = self.font.render(f"R{r.id} [{status}] Data:{r.shared_counter}", True, col)
            self.screen.blit(txt, (px, 40 + i*22))

        # UI LEGEND
        lx, ly = px, 200
        self.screen.blit(self.font.render("LEGEND:", True, BLACK), (lx, ly))
        pygame.draw.rect(self.screen, GREEN, (lx, ly+20, 15, 15))
        self.screen.blit(self.font.render("- Running", True, BLACK), (lx+20, ly+20))
        pygame.draw.rect(self.screen, YELLOW, (lx, ly+40, 15, 15))
        self.screen.blit(self.font.render("- Critical Section", True, BLACK), (lx+20, ly+40))
        pygame.draw.rect(self.screen, RED, (lx, ly+60, 15, 15))
        self.screen.blit(self.font.render("- Failed", True, BLACK), (lx+20, ly+60))

        # SCHEDULER QUEUE (List of waiting processes)
        self.screen.blit(self.font.render("READY QUEUE:", True, BLACK), (px, 300))
        y_q = 320
        for task in list(self.scheduler.ready_queue):
            try:
                rob = task.gi_frame.f_locals.get('robot')
                if rob:
                    q_txt = self.font.render(f"-> Robot {rob.id}", True, BLACK)
                    self.screen.blit(q_txt, (px, y_q))
                    y_q += 18
            except: continue

        pygame.display.flip()