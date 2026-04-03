import matplotlib.pyplot as plt


def display_grid(grid, start, goal, image_file):
    plt.imshow(grid, cmap='binary')
    plt.xticks([])
    plt.yticks([])
    plt.text(start[1], start[0], "A", ha='center', va='center', fontsize=10, color="green")
    plt.text(goal[1], goal[0], "T", ha='center', va='center', fontsize=10, color="red")
    plt.savefig(image_file)
    plt.close()


def display_grid_path(grid, start, goal, path, expanded_list, image_file):
    plt.imshow(grid, cmap='binary')
    plt.xticks([])
    plt.yticks([])

    if expanded_list:
        y = [cell[0] for cell in expanded_list]
        x = [cell[1] for cell in expanded_list]
        plt.scatter(x, y, s=4)

    if path:
        y = [cell[0] for cell in path]
        x = [cell[1] for cell in path]
        plt.plot(x, y, linewidth=2)

    plt.text(start[1], start[0], "A", ha='center', va='center', fontsize=6, color="green")
    plt.text(goal[1], goal[0], "T", ha='center', va='center', fontsize=6, color="red")
    plt.savefig(image_file)
    plt.close()
