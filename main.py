import pygame
import math
from queue import PriorityQueue
import random
import time

WIDTH, HEIGHT = 800, 600
GRID_SIZE = 600
ROWS = 30
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Pathfinding Agent")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

pygame.font.init()
FONT = pygame.font.SysFont("Arial", 16)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.width = width
        self.total_rows = total_rows
        self.neighbors = []

    def get_pos(self):
        return self.row, self.col
    def is_obstacle(self):
        return self.color == RED
    def reset(self):
        self.color = WHITE
    def make_start(self):
        self.color = ORANGE
    def make_goal(self):
        self.color = PURPLE
    def make_obstacle(self):
        self.color = RED
    def make_visited(self):
        self.color = BLUE
    def make_frontier(self):
        self.color = YELLOW
    def make_path(self):
        self.color = GREEN
    def make_agent(self):
        self.color = CYAN
    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))
    
    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_obstacle():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_obstacle():
            self.neighbors.append(grid[self.row][self.col - 1])

def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw_func):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
        current.make_path()
        draw_func()
    return path[::-1]

def search_algorithm(draw_func, grid, start, goal, is_astar):
    start_time = time.time()
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {node: float("inf") for row in grid for node in row}
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}
    f_score[start] = h(start.get_pos(), goal.get_pos())
    
    open_set_hash = {start}
    nodes_expanded = 0

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == goal:
            path = reconstruct_path(came_from, goal, draw_func)
            goal.make_goal()
            exec_time = (time.time() - start_time) * 1000
            return path, nodes_expanded, exec_time

        nodes_expanded += 1
        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1
            
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                
                h_cost = h(neighbor.get_pos(), goal.get_pos())
                f_score[neighbor] = (temp_g_score + h_cost) if is_astar else h_cost
                
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_frontier()
        
        draw_func()
        if current != start:
            current.make_visited()

    return None, nodes_expanded, (time.time() - start_time) * 1000

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid_lines(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width, stats):
    win.fill(WHITE)
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid_lines(win, rows, width)
    
    pygame.draw.rect(win, BLACK, (GRID_SIZE, 0, WIDTH - GRID_SIZE, HEIGHT))
    texts = ["Controls:", "Left Click: Place Nodes", "Right Click: Erase", "A: Run A*", "G: Run Greedy", "C: Clear Board", "R: Random Map", "SPACE: Start Dynamic Agent", "", "Stats:", f"Nodes Explored: {stats['nodes']}", f"Path Cost: {stats['cost']}", f"Time (ms): {stats['time']:.2f}"]
    for i, t in enumerate(texts):
        render = FONT.render(t, True, WHITE)
        win.blit(render, (GRID_SIZE + 10, 20 + i * 25))
    
    pygame.display.update()

def reset_search_colors(grid, start, goal):
    for row in grid:
        for node in row:
            if node.color in [YELLOW, BLUE, GREEN, CYAN]:
                node.reset()
    start.make_start()
    goal.make_goal()

def main():
    grid = make_grid(ROWS, GRID_SIZE)
    start, goal = None, None
    run = True
    stats = {"nodes": 0, "cost": 0, "time": 0.0}
    current_path = []

    while run:
        draw(WIN, grid, ROWS, GRID_SIZE, stats)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                if pos[0] < GRID_SIZE:
                    row, col = pos[0] // (GRID_SIZE // ROWS), pos[1] // (GRID_SIZE // ROWS)
                    node = grid[row][col]
                    if not start and node != goal:
                        start = node
                        start.make_start()
                    elif not goal and node != start:
                        goal = node
                        goal.make_goal()
                    elif node != start and node != goal:
                        node.make_obstacle()

            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if pos[0] < GRID_SIZE:
                    row, col = pos[0] // (GRID_SIZE // ROWS), pos[1] // (GRID_SIZE // ROWS)
                    node = grid[row][col]
                    node.reset()
                    if node == start: start = None
                    if node == goal: goal = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a or event.key == pygame.K_g:
                    if start and goal:
                        for row in grid:
                            for node in row: node.update_neighbors(grid)
                        reset_search_colors(grid, start, goal)
                        is_astar = (event.key == pygame.K_a)
                        path, nodes, t = search_algorithm(lambda: draw(WIN, grid, ROWS, GRID_SIZE, stats), grid, start, goal, is_astar)
                        if path:
                            current_path = path
                            stats = {"nodes": nodes, "cost": len(path), "time": t}

                if event.key == pygame.K_SPACE and current_path:
                    agent_pos = 0
                    while agent_pos < len(current_path):
                        if agent_pos > 0: current_path[agent_pos-1].make_path()
                        agent_node = current_path[agent_pos]
                        agent_node.make_agent()
                        draw(WIN, grid, ROWS, GRID_SIZE, stats)
                        pygame.time.delay(100)

                        if random.random() < 0.1:
                            r_row, r_col = random.randint(0, ROWS-1), random.randint(0, ROWS-1)
                            spawn_node = grid[r_row][r_col]
                            if spawn_node not in [start, goal, agent_node] and not spawn_node.is_obstacle():
                                spawn_node.make_obstacle()
                                if spawn_node in current_path[agent_pos:]:
                                    reset_search_colors(grid, agent_node, goal)
                                    for row in grid:
                                        for n in row: n.update_neighbors(grid)
                                    new_path, n_exp, t = search_algorithm(lambda: draw(WIN, grid, ROWS, GRID_SIZE, stats), grid, agent_node, goal, True)
                                    if new_path:
                                        current_path = new_path
                                        agent_pos = 0
                                        stats["nodes"] += n_exp
                                    else:
                                        print("No path available!")
                                        break
                        agent_pos += 1

                if event.key == pygame.K_c:
                    start, goal = None, None
                    grid = make_grid(ROWS, GRID_SIZE)
                    stats = {"nodes": 0, "cost": 0, "time": 0.0}

                if event.key == pygame.K_r:
                    start, goal = None, None
                    grid = make_grid(ROWS, GRID_SIZE)
                    for row in grid:
                        for node in row:
                            if random.random() < 0.3:
                                node.make_obstacle()

    pygame.quit()

if __name__ == "__main__":
    main()