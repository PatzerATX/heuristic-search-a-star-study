import time

from maze.grid import load_grid, random_grid, save_data
from maze.pathfinding import (
    astar,
    repeated_adaptive_astar,
    repeated_astar_backward,
    repeated_astar_forward,
)
from maze.render import display_grid, display_grid_path


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

        for i in range(maze_count):
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
