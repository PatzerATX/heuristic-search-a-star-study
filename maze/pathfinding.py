from queue import PriorityQueue

from .grid import empty_grid, find_all_neighbors, find_valid_neighbors


def heuristic(current, goal):
    return abs(goal[0] - current[0]) + abs(goal[1] - current[1])


def astar(grid, start, goal, tiebreak):  # accepts a grid, start tuple, goal tuple and a tiebreak value
    open_list = PriorityQueue()  # open_list stores nodes to be expanded in priority of f value.
    open_list.put((0 + heuristic(start, goal), 0, start))  # start cell f value, g value (0), and location added to open_list
    closed_list = set()  # closed_list is initiated as empty. Will store expanded nodes
    came_from = {}  # a dictionary of each node and its updated predecessor
    g_value = {start: 0}  # dictionary of g values. start=0
    expanded_nodes_counter = 0  # counting expanded nodes for statistics reporting
    while not open_list.empty():  # while there are nodes in the open list, continue loop
        f_value, g_tiebreak_current, current = open_list.get()  # priority cell popped from priority queue
        if current in closed_list:  # if current cell has already been expanded, skip it
            continue
        if current == goal:  # if current = goal, run path collection loop
            path = []  # create open empty path list
            while current != start:  # while current node does not = starting point
                path.append(current)  # add current node to path list
                current = came_from[current]  # change current to parent of current
            path.append(start)  # after pathway is created, add the starting point
            return path[::-1], closed_list, expanded_nodes_counter  # return path in opposite order and number of expanded nodes
        closed_list.add(current)  # if current != goal, current is expanded and added to the closed list
        expanded_nodes_counter += 1  # expanded nodes counter incremented by 1
        for neighbor in find_valid_neighbors(grid, current):  # each valid neighbor (not blocked) of current node is traversed
            if neighbor in closed_list:  # if node is already expanded, skip it
                continue
            if (neighbor not in g_value) or (g_value[current] + 1 < g_value[neighbor]):
                # if node doesn't have a g value (hasn't been evaluated) or its g value is greater than this evaluated g value
                g_value[neighbor] = g_value[current] + 1  # g_value is updated to 1 + current (1 move past current)
                came_from[neighbor] = current  # parent of neighbor is set to current
                open_list.put((g_value[neighbor] + heuristic(neighbor, goal), tiebreak * g_value[neighbor], neighbor))
                # neighbor added to open_list (f value, -g value(for tie breaking - choose largest g value), location)
    return None, closed_list, expanded_nodes_counter  # return for failed maze


def repeated_astar_forward(complete_grid, start, goal, tiebreak):
    known_grid = empty_grid()
    complete_path = [start]
    expanded_cells_set = set()
    expanded_nodes_counter = 0
    current = start
    for n in find_all_neighbors(current):
        known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]]  # knowledge of neighbors added to known_grid
    while current != goal:  # while goal not found, continue path finding algorithm
        path, expanded_cells, expanded_nodes_count = astar(known_grid, current, goal, tiebreak)  # astar run from current
        expanded_nodes_counter += expanded_nodes_count
        expanded_cells_set |= expanded_cells  # expanded cells not in expanded_cells_set are added to be passed on each run
        if path is None:
            return None, expanded_cells_set, expanded_nodes_counter
        for cell in path[1:]:  # if path is found, cell after starting point is evaluated
            if complete_grid[cell[0]][cell[1]] == 1:  # if cell is blocked, update known_grid
                known_grid[cell[0]][cell[1]] = 1
                break  # leave loop since path blocked, run a* again from current location with updated knowledge
            current = cell  # otherwise, move to cell
            complete_path.append(current)  # add cell to path list
            for n in find_all_neighbors(current):  # knowledge of neighbors is updated
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


def adaptive_astar(grid, start, goal, h_values):  # accepts a grid, a start tuple, a goal tuple, and the set of h values
    open_list = PriorityQueue()  # open_list stores nodes to be expanded by priority of f values
    if start in h_values:  # if start location already has a calculated h value, use it when node added to priority queue
        open_list.put((h_values[start], 0, start))
    else:  # if start location doesn't have an h value, calculate the Manhattan value
        open_list.put((heuristic(start, goal), 0, start))  # f value, g value (0), and location added to open_list
    closed_list = set()  # closed_list initiated as empty. Will store expanded nodes
    came_from = {}  # a dictionary of each node and it's updated predecessor
    g_values = {start: 0}  # a dictionary of g values. start = 0
    expanded_nodes_counter = 0  # tracks number of expanded nodes for statistics collection
    while not open_list.empty():  # while there are nodes in the open list, continue loop
        f_value, g_tiebreak_current, current = open_list.get()  # cell popped from priority queue
        if current in closed_list:  # if cell has already been expanded, skip
            continue
        if current == goal:  # if current = goal, run path collection loop
            path = []  # create open empty path list
            while current != start:  # while current node does not = starting point
                path.append(current)  # add current node to path list
                current = came_from[current]  # change current to parent of current
            path.append(start)  # after pathway is created, add the starting point
            return path[::-1], closed_list, g_values, expanded_nodes_counter  # return path in opposite order
        closed_list.add(current)  # if current != goal, current is expanded and added to the closed list
        expanded_nodes_counter += 1  # expanded nodes counter incremented by 1
        for neighbor in find_valid_neighbors(grid, current):  # each valid neighbor (not blocked) of current node is traversed
            if neighbor in closed_list:  # if neighbor is already expanded, skip it
                continue
            if (neighbor not in g_values) or (g_values[current] + 1 < g_values[neighbor]):
                # if node doesn't have a g value (hasn't been evaluated) or its g value is greater than this evaluated g value
                g_values[neighbor] = g_values[current] + 1  # g_value is updated to 1 + current (1 move past current)
                came_from[neighbor] = current  # parent of neighbor is set to current
                if neighbor in h_values:  # if node already has a calculated h value
                    open_list.put(((g_values[neighbor] + h_values[neighbor]), -g_values[neighbor], neighbor))
                    # f value calculated as the g value + the current h value
                else:  # if node needs an initial h value calculated
                    open_list.put((g_values[neighbor] + heuristic(neighbor, goal), -g_values[neighbor], neighbor))
                # f value calculated as the g value + the Manhattan distance
    return None, closed_list, g_values, expanded_nodes_counter  # return for maze failure


def repeated_adaptive_astar(complete_grid, start, goal):
    known_grid = empty_grid()
    complete_path = [start]
    h_values_new = {}
    expanded_nodes_counter = 0
    expanded_cells_set = set()
    current = start
    for n in find_all_neighbors(current):  # knowledge of neighbors is updated
        known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]]
    while current != goal:  # while target not discovered yet, continue pathfinding loop
        path, closed_list, g_values, expanded_nodes = adaptive_astar(known_grid, current, goal, h_values_new)
        # adaptive astar run from current (starting) location with updated h values
        expanded_nodes_counter += expanded_nodes
        expanded_cells_set |= closed_list  # expanded cells not in expanded_cells_set are added to be passed on each run
        if path is None:
            return None, expanded_cells_set, expanded_nodes_counter
        for cell in closed_list:  # each expanded cell on this run is accessed
            h_values_new[cell] = g_values[goal] - g_values[cell]  # new h value is calculated as distance from cell to goal
        for cell in path[1:]:  # next cell after start is evaluated
            if complete_grid[cell[0]][cell[1]] == 1:
                known_grid[cell[0]][cell[1]] = 1
                break  # if cell is blocked, update knowledge, and rerun adaptive a*
            current = cell  # move to cell
            complete_path.append(current)  # add cell to path
            for n in find_all_neighbors(current):  # update knowledge of neighbors
                known_grid[n[0]][n[1]] = complete_grid[n[0]][n[1]]
    return complete_path, expanded_cells_set, expanded_nodes_counter
