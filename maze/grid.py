import random

from .constants import HEIGHT, WIDTH


def random_grid():
    from .pathfinding import astar

    while True:
        grid = []
        for r in range(HEIGHT):
            row = []
            for c in range(WIDTH):
                if random.random() < 0.3:
                    row.append(1)
                else:
                    row.append(0)
            grid.append(row)
        while True:
            sr = random.randint(0, HEIGHT - 1)
            sc = random.randint(0, WIDTH - 1)
            if grid[sr][sc] == 0:
                start = (sr, sc)
                break
        while True:
            fr = random.randint(0, HEIGHT - 1)
            fc = random.randint(0, WIDTH - 1)
            if grid[fr][fc] == 0 and (fr, fc) != (sr, sc):
                goal = (fr, fc)
                break

        path, _expanded, _count = astar(grid, start, goal, -1)
        if path:
            return grid, start, goal


def empty_grid():
    grid = []
    for r in range(HEIGHT):
        row = []
        for c in range(WIDTH):
            row.append(0)
        grid.append(row)
    return grid


def find_valid_neighbors(grid, current):
    r, c = current
    possible_neighbors = [(r + 1, c), (r - 1, c), (r, c - 1), (r, c + 1)]
    neighbors = []
    for r, c in possible_neighbors:
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            if grid[r][c] == 0:
                neighbors.append((r, c))
    return neighbors


def find_all_neighbors(current):
    r, c = current
    possible_neighbors = [(r + 1, c), (r - 1, c), (r, c - 1), (r, c + 1)]
    neighbors = []
    for r, c in possible_neighbors:
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            neighbors.append((r, c))
    return neighbors


def load_grid(data_file):
    with open(data_file, 'r') as f:
        start_line = f.readline().strip().strip("()")
        goal = f.readline().strip().strip("()")
        start_values = start_line.split(",")
        goal_values = goal.split(",")
        start = (int(start_values[0]), int(start_values[1]))
        goal = (int(goal_values[0]), int(goal_values[1]))
        grid = []
        for line in f:
            row = [int(num) for num in line.strip()]
            grid.append(row)
    return grid, start, goal


def save_data(grid, start, goal, data_file):
    file = open(data_file, 'w')
    file.write(str(start) + "\n")
    file.write(str(goal) + "\n")
    for r in range(HEIGHT):
        for c in range(WIDTH):
            file.write(str(grid[r][c]))
        file.write("\n")
    file.close()
