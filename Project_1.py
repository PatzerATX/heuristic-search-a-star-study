import random
import time
from queue import PriorityQueue
import matplotlib.pyplot as plt

HEIGHT = 51
WIDTH = 51

def random_grid():
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
    possible_neighbors = [(r+1, c), (r-1, c), (r, c-1), (r, c+1)]
    neighbors = []
    for r, c in possible_neighbors:
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            if grid[r][c] == 0:
                neighbors.append((r, c))
    return neighbors

def find_all_neighbors(current):
    r, c = current
    possible_neighbors = [(r+1, c), (r-1, c), (r, c-1), (r, c+1)]
    neighbors = []
    for r, c in possible_neighbors:
        if 0 <= r < HEIGHT and 0 <= c < WIDTH:
            neighbors.append((r, c))
    return neighbors

def heuristic(current, goal):
    return abs(goal[0] - current[0]) + abs(goal[1] - current[1])

def load_grid(data_file):
    with open(data_file, 'r' ) as f:
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

def display_grid(grid, start, goal, image_file):
    plt.imshow(grid, cmap='binary')
    plt.xticks([])
    plt.yticks([])
    plt.text(start[1], start[0], "A", ha = 'center', va = 'center', fontsize = 10, color = "green")
    plt.text(goal[1], goal[0], "T", ha = 'center', va = 'center', fontsize = 10, color = "red")
    plt.savefig(image_file)
    plt.close()

def display_grid_path(grid, start, goal, path, expanded_list, image_file):
    plt.imshow(grid, cmap='binary')
    plt.xticks([])
    plt.yticks([])

    if expanded_list:
        y = [cell[0] for cell in expanded_list]
        x = [cell[1] for cell in expanded_list]
        plt.scatter(x, y, s = 4)

    if path:
        y = [cell[0] for cell in path]
        x = [cell[1] for cell in path]
        plt.plot(x, y, linewidth = 2)

    plt.text(start[1], start[0], "A", ha='center', va='center', fontsize=6, color="green")
    plt.text(goal[1], goal[0], "T", ha='center', va='center', fontsize=6, color="red")

    plt.savefig(image_file)
    plt.close()

def astar(grid, start, goal, tiebreak): #accepts a grid, start tuple, goal tuple and a tiebreak value
    open_list = PriorityQueue() #open_list stores nodes to be expanded in priority of f value.
    open_list.put((0 + heuristic(start, goal), 0, start)) #start cell f value, g value (0), and location added to open_list
    closed_list = set() #closed_list is initiated as empty. Will store expanded nodes
    came_from = {} #a dictionary of each node and its updated predecessor
    g_value = {start: 0} #dictionary of g values. start=0
    expanded_nodes_counter = 0 #counting expanded nodes for statistics reporting
    while not open_list.empty(): #while there are nodes in the open list, continue loop
        f_value, g_tiebreak_current, current = open_list.get() #priority cell popped from priority queue
        if current in closed_list: #if current cell has already been expanded, skip it
            continue
        if current == goal: #if current = goal, run path collection loop
            path = [] #create open empty path list
            while current != start: #while current node does not = starting point
                path.append(current) #add current node to path list
                current = came_from[current] #change current to parent of current
            path.append(start) #after pathway is created, add the starting point
            return path[::-1], closed_list, expanded_nodes_counter #return path in opposite order and number of expanded nodes
        closed_list.add(current) #if current != goal, current is expanded and added to the closed list
        expanded_nodes_counter += 1 #expanded nodes counter incremented by 1
        for neighbor in find_valid_neighbors(grid, current): #each valid neighbor (not blocked) of current node is traversed
            if neighbor in closed_list: #if node is already expanded, skip it
                continue
            if (neighbor not in g_value) or (g_value[current] + 1 < g_value[neighbor]):
            #if node doesn't have a g value (hasn't been evaluated) or its g value is greater than this evaluated g value
                g_value[neighbor] = g_value[current] + 1 #g_value is updated to 1 + current (1 move past current)
                came_from[neighbor] = current #parent of neighbor is set to current
                open_list.put((g_value[neighbor] + heuristic(neighbor, goal), tiebreak * g_value[neighbor], neighbor))
                #neighbor added to open_list (f value, -g value(for tie breaking - choose largest g value), location)
    return None, closed_list, expanded_nodes_counter #return for failed maze

def repeated_astar_forward(complete_grid, start, goal, tiebreak):
    known_grid = empty_grid()
    complete_path = [start]
    expanded_cells_set = set()
    expanded_nodes_counter = 0
    current = start
    for n in find_all_neighbors(current):
        known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]] #knowledge of neighbors added to known_grid
    while current != goal: #while goal not found, continue path finding algorithm
        path, expanded_cells, expanded_nodes_count = astar(known_grid, current, goal, tiebreak) #astar run from current
        expanded_nodes_counter += expanded_nodes_count
        expanded_cells_set |= expanded_cells #expanded cells not in expanded_cells_set are added to be passed on each run
        if path is None:
            return None, expanded_cells_set, expanded_nodes_counter
        for cell in path[1:]: #if path is found, cell after starting point is evaluated
            if complete_grid[cell[0]][cell[1]] == 1: #if cell is blocked, update known_grid
                known_grid[cell[0]][cell[1]] = 1
                break #leave loop since path blocked, run a* again from current location with updated knowledge
            current = cell #otherwise, move to cell
            complete_path.append(current) #add cell to path list
            for n in find_all_neighbors(current): #knowledge of neighbors is updated
                known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]]
    return complete_path, expanded_cells_set, expanded_nodes_counter

def repeated_astar_backward(complete_grid, start, goal):
    known_grid = empty_grid()
    complete_path = [start]
    expanded_cells_set = set()
    expanded_nodes_counter = 0
    current = start
    for n in find_all_neighbors(current):
        known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]]
    while current != goal:
        path, expanded_cells, expanded_nodes_count = astar(known_grid, goal, current, -1)
        expanded_nodes_counter += expanded_nodes_count
        expanded_cells_set |= expanded_cells
        if path is None:
            return None, expanded_cells_set, expanded_nodes_counter
        path = path[::-1]
        for cell in path[1:]:
            if complete_grid[cell[0]][cell[1]] == 1:
                known_grid[cell[0]][cell[1]] = 1
                break
            current = cell
            complete_path.append(current)
            for n in find_all_neighbors(current):
                known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]]
    return complete_path, expanded_cells_set, expanded_nodes_counter

def adaptive_astar(grid, start, goal, h_values): #accepts a grid, a start tuple, a goal tuple, and the set of h values
    open_list = PriorityQueue() #open_list stores nodes to be expanded by priority of f values
    if start in h_values: #if start location already has a calculated h value, use it when node added to priority queue
        open_list.put((h_values[start], 0, start))
    else: #if start location doesn't have an h value, calculate the Manhattan value
        open_list.put((heuristic(start, goal), 0, start)) #f value, g value (0), and location added to open_list
    closed_list = set() #closed_list initiated as empty. Will store expanded nodes
    came_from = {} #a dictionary of each node and it's updated predecessor
    g_values = {start: 0} #a dictionary of g values. start = 0
    expanded_nodes_counter = 0 #tracks number of expanded nodes for statistics collection
    while not open_list.empty(): #while there are nodes in the open list, continue loop
        f_value, g_tiebreak_current, current = open_list.get() #cell popped from priority queue
        if current in closed_list: #if cell has already been expanded, skip
            continue
        if current == goal: #if current = goal, run path collection loop
            path = [] #create open empty path list
            while current != start: #while current node does not = starting point
                path.append(current) #add current node to path list
                current = came_from[current] #change current to parent of current
            path.append(start) #after pathway is created, add the starting point
            return path[::-1], closed_list, g_values, expanded_nodes_counter #return path in opposite order
        closed_list.add(current) #if current != goal, current is expanded and added to the closed list
        expanded_nodes_counter += 1 #expanded nodes counter incremented by 1
        for neighbor in find_valid_neighbors(grid, current): #each valid neighbor (not blocked) of current node is traversed
            if neighbor in closed_list: #if neighbor is already expanded, skip it
                continue
            if (neighbor not in g_values) or (g_values[current] + 1 < g_values[neighbor]):
            #if node doesn't have a g value (hasn't been evaluated) or its g value is greater than this evaluated g value
                g_values[neighbor] = g_values[current] + 1 #g_value is updated to 1 + current (1 move past current)
                came_from[neighbor] = current #parent of neighbor is set to current
                if neighbor in h_values: #if node already has a calculated h value
                    open_list.put(((g_values[neighbor] + h_values[neighbor]), -g_values[neighbor], neighbor))
                    #f value calculated as the g value + the current h value
                else: #if node needs an initial h value calculated
                    open_list.put((g_values[neighbor] + heuristic(neighbor, goal), -g_values[neighbor], neighbor))
                #f value calculated as the g value + the Manhattan distance
    return (None, closed_list, g_values, expanded_nodes_counter) #return for maze failure

def repeated_adaptive_astar(complete_grid, start, goal):
    known_grid = empty_grid()
    complete_path = [start]
    h_values_new = {}
    expanded_nodes_counter = 0
    expanded_cells_set = set()
    current = start
    for n in find_all_neighbors(current): #knowledge of neighbors is updated
        known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]]
    while current != goal: #while target not discovered yet, continue pathfinding loop
        path, closed_list, g_values, expanded_nodes = adaptive_astar(known_grid, current, goal, h_values_new)
        #adaptive astar run from current (starting) location with updated h values
        expanded_nodes_counter += expanded_nodes
        expanded_cells_set |= closed_list #expanded cells not in expanded_cells_set are added to be passed on each run
        if path is None:
            return None, expanded_cells_set, expanded_nodes_counter
        for cell in closed_list: #each expanded cell on this run is accessed
            h_values_new[cell] = g_values[goal] - g_values[cell] #new h value is calculated as distance from cell to goal
        for cell in path[1:]: #next cell after start is evaluated
            if complete_grid[cell[0]][cell[1]] == 1:
                known_grid[cell[0]][cell[1]] = 1
                break #if cell is blocked, update knowledge, and rerun adaptive a*
            current = cell #move to cell
            complete_path.append(current) #add cell to path
            for n in find_all_neighbors(current): #update knowledge of neighbors
                known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]]
    return complete_path, expanded_cells_set, expanded_nodes_counter

def main():

    print()
    shared_maze = input("Create random mazes for simulation? y/n ")
    if shared_maze == "y":
        maze_count = int(input("How many mazes would you like to generate? "))

        total_astar_nodes_expanded = 0
        total_astar_path_length = 0
        total_astar_runtime = 0
        total_repeated_astar_forward_HIGH_nodes_expanded = 0
        total_repeated_astar_forward_HIGH_path_length = 0
        total_repeated_astar_forward_HIGH_runtime = 0
        total_repeated_astar_forward_LOW_nodes_expanded = 0
        total_repeated_astar_forward_LOW_path_length = 0
        total_repeated_astar_forward_LOW_runtime = 0
        total_repeated_astar_backward_nodes_expanded = 0
        total_repeated_astar_backward_path_length = 0
        total_repeated_astar_backward_runtime = 0
        total_adaptive_astar_nodes_expanded = 0
        total_adaptive_astar_path_length = 0
        total_adaptive_astar_runtime = 0
        maze_fails = 0

        for i in range (maze_count):
            grid, start, goal = random_grid()
            data_file = "maze" + str(i) + ".txt"
            image_file = "maze" + str(i) + ".png"
            save_data(grid, start, goal, data_file)
            display_grid(grid, start, goal, image_file)
            print(data_file, "generated")

            astar_start_time = time.time()
            path, expanded_cells, astar_nodes_expanded = astar(grid, start, goal, -1)
            astar_end_time = time.time()
            astar_path_length = len(path) if path else 0
            display_grid_path(grid, start, goal, path, expanded_cells, f"maze{i}_astar_path.png")

            repeated_forward_HIGH_astar_start_time = time.time()
            path, expanded_cells, repeated_forward_HIGH_astar_nodes_expanded = repeated_astar_forward(grid, start, goal, -1)
            repeated_forward_HIGH_astar_end_time = time.time()
            repeated_forward_HIGH_astar_path_length = len(path) if path else 0
            display_grid_path(grid, start, goal, path, expanded_cells, f"maze{i}_forward_HIGH_path.png")

            repeated_forward_LOW_astar_start_time = time.time()
            path, expanded_cells, repeated_forward_LOW_astar_nodes_expanded = repeated_astar_forward(grid, start, goal, 1)
            repeated_forward_LOW_astar_end_time = time.time()
            repeated_forward_LOW_astar_path_length = len(path) if path else 0
            display_grid_path(grid, start, goal, path, expanded_cells, f"maze{i}_forward_LOW_path.png")

            repeated_astar_backward_start_time = time.time()
            path, expanded_cells, repeated_backward_astar_nodes_expanded = repeated_astar_backward(grid, start, goal)
            repeated_astar_backward_end_time = time.time()
            repeated_astar_backward_path_length = len(path) if path else 0
            display_grid_path(grid, start, goal, path, expanded_cells, f"maze{i}_backward_path.png")

            adaptive_astar_start_time = time.time()
            path, expanded_cells, adaptive_astar_nodes_expanded = repeated_adaptive_astar(grid, start, goal)
            adaptive_astar_end_time = time.time()
            adaptive_astar_path_length = len(path) if path else 0
            display_grid_path(grid, start, goal, path, expanded_cells, f"maze{i}_adaptive_path.png")

            if not path:
                maze_fails += 1
            else:
                total_astar_nodes_expanded += astar_nodes_expanded
                total_astar_path_length += astar_path_length
                total_astar_runtime += (astar_end_time - astar_start_time)
                total_repeated_astar_forward_HIGH_nodes_expanded += repeated_forward_HIGH_astar_nodes_expanded
                total_repeated_astar_forward_HIGH_path_length += repeated_forward_HIGH_astar_path_length
                total_repeated_astar_forward_HIGH_runtime += (repeated_forward_HIGH_astar_end_time - repeated_forward_HIGH_astar_start_time)
                total_repeated_astar_forward_LOW_nodes_expanded += repeated_forward_LOW_astar_nodes_expanded
                total_repeated_astar_forward_LOW_path_length += repeated_forward_LOW_astar_path_length
                total_repeated_astar_forward_LOW_runtime += (repeated_forward_LOW_astar_end_time - repeated_forward_LOW_astar_start_time)
                total_repeated_astar_backward_nodes_expanded += repeated_backward_astar_nodes_expanded
                total_repeated_astar_backward_path_length += repeated_astar_backward_path_length
                total_repeated_astar_backward_runtime += (repeated_astar_backward_end_time - repeated_astar_backward_start_time)
                total_adaptive_astar_nodes_expanded += adaptive_astar_nodes_expanded
                total_adaptive_astar_path_length += adaptive_astar_path_length
                total_adaptive_astar_runtime += (adaptive_astar_end_time - adaptive_astar_start_time)
        print()
        print("A* statistics:")
        print("Average Expanded Nodes: ", round(total_astar_nodes_expanded / (maze_count - maze_fails)))
        print("Average Path Length: ", round(total_astar_path_length / (maze_count - maze_fails)))
        print("Average Runtime: ", total_astar_runtime / (maze_count - maze_fails))
        print()

        print("Repeated Forward HIGH A* statistics:")
        print("Average Expanded Nodes: ", round(total_repeated_astar_forward_HIGH_nodes_expanded / (maze_count - maze_fails)))
        print("Average Path Length: ", round(total_repeated_astar_forward_HIGH_path_length / (maze_count - maze_fails)))
        print("Average Runtime: ", total_repeated_astar_forward_HIGH_runtime / (maze_count - maze_fails))
        print()

        print("Repeated Forward LOW A* statistics:")
        print("Average Expanded Nodes: ", round(total_repeated_astar_forward_LOW_nodes_expanded / (maze_count - maze_fails)))
        print("Average Path Length: ", round(total_repeated_astar_forward_LOW_path_length / (maze_count - maze_fails)))
        print("Average Runtime: ", total_repeated_astar_forward_LOW_runtime / (maze_count - maze_fails))
        print()

        print("Repeated Backward A* statistics:")
        print("Average Expanded Nodes: ", round(total_repeated_astar_backward_nodes_expanded / (maze_count - maze_fails)))
        print("Average Path Length: ", round(total_repeated_astar_backward_path_length / (maze_count - maze_fails)))
        print("Average Runtime: ", total_repeated_astar_backward_runtime / (maze_count - maze_fails))
        print()

        print("Adaptive A* statistics:")
        print("Average Expanded Nodes: ", round(total_adaptive_astar_nodes_expanded / (maze_count - maze_fails)))
        print("Average Path Length: ", round(total_adaptive_astar_path_length / (maze_count - maze_fails)))
        print("Average Runtime: ", total_adaptive_astar_runtime / (maze_count - maze_fails))
        print()

        print("Failed Mazes: ", maze_fails)

    else:
        print()
        print("Running simulation on stored maze.")
        maze_file_name = input("Maze file name: ")
        print()

        grid, start, goal = load_grid(maze_file_name)

        start_time = time.time()
        path, expanded_cells, expanded_nodes_count = astar(grid, start, goal, -1)
        end_time = time.time()
        print("Maze", maze_file_name, "A* statistics:")
        print("Nodes expanded: ", expanded_nodes_count)
        print("Path length: ", len(path) if path else "No path found")
        print("Runtime: ", end_time - start_time)
        print()
        display_grid_path(grid, start, goal, path, expanded_cells, f"{maze_file_name}_A*_path.png")

        start_time = time.time()
        path, expanded_cells, expanded_nodes_count = repeated_astar_forward(grid, start, goal, -1)
        end_time = time.time()
        print("Maze", maze_file_name, "Repeated Forward A* statistics:")
        print("Nodes expanded: ", expanded_nodes_count)
        print("Path length: ", len(path) if path else "No path found")
        print("Runtime: ", end_time - start_time)
        print()
        display_grid_path(grid, start, goal, path, expanded_cells, f"{maze_file_name}_RepeatedForward_path.png")

        start_time = time.time()
        path, expanded_cells, expanded_nodes_count = repeated_astar_backward(grid, start, goal)
        end_time = time.time()
        print("Maze", maze_file_name, "Repeated Backward A* statistics:")
        print("Nodes expanded: ", expanded_nodes_count)
        print("Path length: ", len(path) if path else "No path found")
        print("Runtime: ", end_time - start_time)
        print()
        display_grid_path(grid, start, goal, path, expanded_cells, f"{maze_file_name}_RepeatedBackward_path.png")

        start_time = time.time()
        path, expanded_cells, expanded_nodes_count = repeated_adaptive_astar(grid, start, goal)
        end_time = time.time()
        print("Maze", maze_file_name, "Adaptive A* statistics:")
        print("Nodes expanded: ", expanded_nodes_count)
        print("Path length: ", len(path) if path else "No path found")
        print("Runtime: ", end_time - start_time)
        print()
        display_grid_path(grid, start, goal, path, expanded_cells, f"{maze_file_name}_Adaptive_path.png")

if __name__ == '__main__':
    main()
