import pygame
import sys
import time
import heapq
from collections import deque

# Constants
WIDTH, HEIGHT = 800, 600
GRID_WIDTH = 600
MENU_WIDTH = WIDTH - GRID_WIDTH
ROWS, COLS = 10, 10
CELL_SIZE = GRID_WIDTH // COLS

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
START_COLOR = (138, 43, 226)
END_COLOR = (255, 0, 0)
OBSTACLE_COLOR = (0, 0, 255)
BUTTON_COLOR = (200, 200, 200)
BUTTON_OUTLINE_COLOR = BLACK
TEXT_COLOR = BLACK
LIGHT_GREY = (211, 211, 211)
SEARCH_COLOR = (145, 145, 145) # light brown
PATH_COLOR = (165, 42, 42)    # brown

# Initialize grid and Pygame
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Robot Pathfinding")

grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]


def draw_grid():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if grid[row][col] == 0 else START_COLOR if grid[row][col] == 1 else END_COLOR if grid[row][col] == 2 else OBSTACLE_COLOR
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, color, rect)
            pygame.draw.rect(window, BLACK, rect, 1)


def draw_menu():
    pygame.draw.rect(window, LIGHT_GREY, (GRID_WIDTH, 0, MENU_WIDTH, HEIGHT))
    font = pygame.font.Font(None, 30)

    buttons = [("Run BFS", 50), ("Run DFS", 100), ("Run UCS", 150)]
    for text, y in buttons:
        button_rect = pygame.Rect(GRID_WIDTH + 20, y, 140, 30)
        pygame.draw.rect(window, BUTTON_COLOR, button_rect)
        pygame.draw.rect(window, BUTTON_OUTLINE_COLOR, button_rect, 2)
        button_text = font.render(text, True, TEXT_COLOR)
        window.blit(button_text, (GRID_WIDTH + 30, y + 5))


def display_time(taken_time):
    font = pygame.font.Font(None, 30)
    time_text = font.render(f"Time: {taken_time:.3f} sec", True, TEXT_COLOR)
    window.blit(time_text, (GRID_WIDTH + 20, 200))


def reset_grid():
    global grid, start_set, end_set, start, end, path_found
    grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    start_set = end_set = False
    start = end = None
    path_found = False
    draw_grid()


def get_neighbors(row, col, rows, cols):
    neighbors = []
    if row > 0: neighbors.append((row - 1, col))
    if row < rows - 1: neighbors.append((row + 1, col))
    if col > 0: neighbors.append((row, col - 1))
    if col < cols - 1: neighbors.append((row, col + 1))
    return neighbors


def reconstruct_path(window, parent, start, end, cell_size):
    current = end
    while current != start:
        row, col = current
        pygame.draw.rect(window, PATH_COLOR, (col * cell_size, row * cell_size, cell_size, cell_size))
        pygame.display.update()
        time.sleep(0.1)
        current = parent[current]


def bfs(grid, start, end, window, cell_size):
    queue = deque([start])
    visited = set([start])
    parent = {}
    while queue:
        current = queue.popleft()
        if current == end:
            reconstruct_path(window, parent, start, end, cell_size)
            return True
        for n_row, n_col in get_neighbors(*current, len(grid), len(grid[0])):
            neighbor = (n_row, n_col)
            if neighbor not in visited and grid[n_row][n_col] != 3:
                queue.append(neighbor)
                visited.add(neighbor)
                parent[neighbor] = current
                visualize(window, neighbor, cell_size)
    return False


def dfs(grid, start, end, window, cell_size):
    stack = [start]
    visited = set([start])
    parent = {}
    while stack:
        current = stack.pop()
        if current == end:
            reconstruct_path(window, parent, start, end, cell_size)
            return True
        for n_row, n_col in get_neighbors(*current, len(grid), len(grid[0])):
            neighbor = (n_row, n_col)
            if neighbor not in visited and grid[n_row][n_col] != 3:
                stack.append(neighbor)
                visited.add(neighbor)
                parent[neighbor] = current
                visualize(window, neighbor, cell_size)
    return False


def ucs(grid, start, end, window, cell_size):
    pq = [(0, start)]
    visited = set([start])
    parent = {}
    cost = {start: 0}
    while pq:
        current_cost, current = heapq.heappop(pq)
        if current == end:
            reconstruct_path(window, parent, start, end, cell_size)
            return True
        for n_row, n_col in get_neighbors(*current, len(grid), len(grid[0])):
            neighbor = (n_row, n_col)
            if neighbor not in visited and grid[n_row][n_col] != 3:
                new_cost = current_cost + 1
                if neighbor not in cost or new_cost < cost[neighbor]:
                    heapq.heappush(pq, (new_cost, neighbor))
                    visited.add(neighbor)
                    parent[neighbor] = current
                    cost[neighbor] = new_cost
                    visualize(window, neighbor, cell_size)
    return False


def visualize(window, cell, cell_size):
    row, col = cell
    pygame.draw.rect(window, SEARCH_COLOR, (col * cell_size, row * cell_size, cell_size, cell_size))
    pygame.display.update()
    time.sleep(0.05)


# Main loop
start_set = end_set = False
start = end = None
running = True
path_found = False
start_time = end_time = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if x < GRID_WIDTH:
                row, col = y // CELL_SIZE, x // CELL_SIZE
                if event.button == 1:
                    if grid[row][col] == 1:
                        grid[row][col] = 0
                        start_set = False
                        start = None
                    elif grid[row][col] == 2:
                        grid[row][col] = 0
                        end_set = False
                        end = None
                    elif grid[row][col] == 3:
                        grid[row][col] = 0
                    elif not start_set:
                        grid[row][col] = 1
                        start = (row, col)
                        start_set = True
                    elif not end_set:
                        grid[row][col] = 2
                        end = (row, col)
                        end_set = True
                elif event.button == 3:
                    grid[row][col] = 3 if grid[row][col] == 0 else 0
            elif GRID_WIDTH <= x < WIDTH:
                if 50 <= y <= 80 and start and end:
                    start_time = time.time()
                    path_found = bfs(grid, start, end, window, CELL_SIZE)
                    end_time = time.time()
                elif 100 <= y <= 130 and start and end:
                    start_time = time.time()
                    path_found = dfs(grid, start, end, window, CELL_SIZE)
                    end_time = time.time()
                elif 150 <= y <= 180 and start and end:
                    start_time = time.time()
                    path_found = ucs(grid, start, end, window, CELL_SIZE)
                    end_time = time.time()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_grid()

    window.fill(WHITE)
    draw_grid()
    draw_menu()
    if start_time and end_time:
        display_time(end_time - start_time)

    pygame.display.update()
