import random
import sys
import time

import pygame

from maze.constants import HEIGHT, WIDTH
from maze.grid import empty_grid, find_all_neighbors, load_grid, random_grid
from maze.pathfinding import adaptive_astar

CELL_SIZE = 16
MARGIN = 0
INFO_PANEL = 60
FPS = 30
COMP_DELAY_MS = 200
GOAL_FLASH_MS = 220
GOAL_FLASH_COUNT = 3
STAR_COUNT = 180
STAR_REVEAL_COUNT = 72
STAR_SEND_SELF_COUNT = 36
STAR_SEND_OPP_COUNT = 36
STAR_PENALTY_COUNT = 36
COMP_REVEAL_NEIGHBORS = 1
PANEL_WIDTH = 320

UNKNOWN = -1
FREE = 0
BLOCKED = 1

COLOR_BG = (8, 8, 8)
COLOR_UNKNOWN = (70, 70, 70)
COLOR_FOG_COMP = (190, 206, 232)
COLOR_FREE = (246, 242, 248)
COLOR_BLOCKED = (40, 40, 50)
COLOR_GRID = (60, 60, 60)
COLOR_START = (120, 180, 150)
COLOR_GOAL = (220, 140, 150)
COLOR_HUMAN = (120, 190, 160)
COLOR_COMP = (0, 0, 0)
COLOR_STAR = (245, 215, 120)
COLOR_FLASH_RED = (255, 110, 110)
COLOR_TEXT = (245, 215, 120)
COLOR_SCORE = (220, 60, 60)
COLOR_STATUS_BG = (245, 215, 120)
COLOR_STATUS_TEXT = (0, 0, 0)


def shade(base, r, c, amount=4):
    return base


def clamp(n, lo, hi):
    return max(lo, min(hi, n))


def init_known_grid():
    return [[UNKNOWN for _ in range(WIDTH)] for _ in range(HEIGHT)]


def reveal_neighbors(known_grid, full_grid, position):
    for r, c in find_all_neighbors(position):
        known_grid[r][c] = full_grid[r][c]


def reveal_cell(known_grid, full_grid, position):
    r, c = position
    known_grid[r][c] = full_grid[r][c]


def merge_known(target_known, source_known):
    for r in range(HEIGHT):
        for c in range(WIDTH):
            if source_known[r][c] != UNKNOWN:
                target_known[r][c] = source_known[r][c]


def reveal_radius(known_grid, full_grid, position, radius):
    pr, pc = position
    for r in range(pr - radius, pr + radius + 1):
        for c in range(pc - radius, pc + radius + 1):
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                known_grid[r][c] = full_grid[r][c]


def reveal_box(known_grid, full_grid, position, size):
    # Reveals a size x size box with the actor near the center (biased top-left for even sizes).
    pr, pc = position
    start_r = pr - (size // 2)
    start_c = pc - (size // 2)
    for r in range(start_r, start_r + size):
        for c in range(start_c, start_c + size):
            if 0 <= r < HEIGHT and 0 <= c < WIDTH:
                known_grid[r][c] = full_grid[r][c]


def flash_cells(screen, clock, grid_surface, panel_surface, goal, human_pos, comp_pos, cells, offset_x):
    if not cells:
        return
    end_time = pygame.time.get_ticks() + 1600
    while pygame.time.get_ticks() < end_time:
        screen.fill(COLOR_BG)
        screen.blit(panel_surface, (0, 0))
        screen.blit(grid_surface, (offset_x, 0))
        for r, c in cells:
            x = offset_x + MARGIN + c * (CELL_SIZE + MARGIN)
            y = MARGIN + r * (CELL_SIZE + MARGIN)
            pygame.draw.rect(screen, COLOR_FLASH_RED, (x, y, CELL_SIZE, CELL_SIZE))
        draw_goal(screen, goal, offset_x)
        draw_agent(screen, human_pos, COLOR_HUMAN, offset_x)
        draw_agent(screen, comp_pos, COLOR_COMP, offset_x)
        pygame.display.flip()
        clock.tick(FPS)


def render_grid_surface(surface, full_grid, human_known, comp_known, start, star_positions):
    surface.fill(COLOR_BG)
    for r in range(HEIGHT):
        for c in range(WIDTH):
            x = MARGIN + c * (CELL_SIZE + MARGIN)
            y = MARGIN + r * (CELL_SIZE + MARGIN)

            if human_known[r][c] == UNKNOWN:
                if comp_known[r][c] != UNKNOWN:
                    color = shade(COLOR_FOG_COMP, r, c, amount=8)
                else:
                    color = shade(COLOR_UNKNOWN, r, c, amount=10)
            else:
                base = COLOR_FREE if human_known[r][c] == FREE else COLOR_BLOCKED
                color = shade(base, r, c, amount=6)

            pygame.draw.rect(surface, color, (x, y, CELL_SIZE, CELL_SIZE))

            if (r, c) in star_positions:
                pygame.draw.circle(surface, COLOR_STAR, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 4)
            if r == start[0] and c == start[1]:
                pygame.draw.circle(surface, COLOR_START, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), CELL_SIZE // 2 - 2)


def render_panel_surface(surface, star_totals, star_used):
    surface.fill((20, 20, 20))
    font = pygame.font.SysFont("arial", 18)
    header = font.render("Star Outcomes", True, COLOR_TEXT)
    surface.blit(header, (12, 12))

    col_name = 12
    col_used = 190
    col_left = 260

    name_hdr = font.render("Type", True, COLOR_TEXT)
    used_hdr = font.render("Used", True, COLOR_TEXT)
    left_hdr = font.render("Left", True, COLOR_TEXT)
    surface.blit(name_hdr, (col_name, 44))
    surface.blit(used_hdr, (col_used, 44))
    surface.blit(left_hdr, (col_left, 44))

    pygame.draw.line(surface, COLOR_TEXT, (12, 68), (PANEL_WIDTH - 12, 68), 1)

    lines = [
        ("Reveal 8x8", "reveal"),
        ("Send Self", "send_self"),
        ("Send Opponent", "send_opp"),
        ("Penalty -1", "penalty"),
    ]
    y = 78
    for label, key in lines:
        total = star_totals[key]
        used = star_used[key]
        remaining = total - used
        surface.blit(font.render(label, True, COLOR_TEXT), (col_name, y))
        surface.blit(font.render(str(used), True, COLOR_TEXT), (col_used, y))
        surface.blit(font.render(str(remaining), True, COLOR_TEXT), (col_left, y))
        y += 26


def draw_goal(screen, goal, offset_x):
    r, c = goal
    x = offset_x + MARGIN + c * (CELL_SIZE + MARGIN)
    y = MARGIN + r * (CELL_SIZE + MARGIN)
    t = pygame.time.get_ticks()
    pulse = 2 + int((t // 160) % 4)
    pygame.draw.circle(
        screen,
        COLOR_GOAL,
        (x + CELL_SIZE // 2, y + CELL_SIZE // 2),
        CELL_SIZE // 2 - 2 + pulse // 2,
    )




def draw_agent(screen, pos, color, offset_x):
    r, c = pos
    x = offset_x + MARGIN + c * (CELL_SIZE + MARGIN)
    y = MARGIN + r * (CELL_SIZE + MARGIN)
    center = (x + CELL_SIZE // 2, y + CELL_SIZE // 2)
    t = pygame.time.get_ticks()
    pulse = 2 + int((t // 160) % 4)  # 2..5 px pulse
    outer_radius = CELL_SIZE // 2
    inner_radius = max(2, outer_radius - 3)
    pygame.draw.circle(screen, (20, 20, 20), center, outer_radius + pulse // 3)
    pygame.draw.circle(screen, color, center, inner_radius + pulse // 2)


def next_human_position(key, current):
    r, c = current
    if key == pygame.K_UP:
        return r - 1, c
    if key == pygame.K_DOWN:
        return r + 1, c
    if key == pygame.K_LEFT:
        return r, c - 1
    if key == pygame.K_RIGHT:
        return r, c + 1
    return current


def find_random_goal(full_grid, human_pos, comp_pos, old_goal=None):
    candidates = []
    for r in range(HEIGHT):
        for c in range(WIDTH):
            if full_grid[r][c] == FREE:
                if (r, c) == human_pos or (r, c) == comp_pos:
                    continue
                if old_goal is not None and (r, c) == old_goal:
                    continue
                candidates.append((r, c))
    if not candidates:
        return old_goal
    return random.choice(candidates)


def run_game(full_grid, start, goal):
    pygame.init()
    grid_width = WIDTH * (CELL_SIZE + MARGIN)
    grid_height = HEIGHT * (CELL_SIZE + MARGIN)
    width_px = PANEL_WIDTH + grid_width
    height_px = grid_height
    screen = pygame.display.set_mode((width_px, height_px))
    pygame.display.set_caption("Maze Duel")
    clock = pygame.time.Clock()
    grid_surface = pygame.Surface((grid_width, grid_height))
    panel_surface = pygame.Surface((PANEL_WIDTH, grid_height))

    human_pos = start
    comp_pos = start

    human_known = init_known_grid()
    comp_known = init_known_grid()
    comp_planning = empty_grid()

    reveal_cell(human_known, full_grid, start)
    reveal_neighbors(human_known, full_grid, start)

    reveal_cell(comp_known, full_grid, start)
    reveal_cell(comp_planning, full_grid, start)

    h_values = {}

    turn = "human"
    winner = None
    human_score = 0
    comp_score = 0
    winning_score = 3
    status_message = ""
    status_until_ms = 0
    star_positions = []
    for r in range(HEIGHT):
        for c in range(WIDTH):
            if full_grid[r][c] == FREE and (r, c) not in (start, goal):
                star_positions.append((r, c))
    random.shuffle(star_positions)
    star_positions = star_positions[:STAR_COUNT]
    random.shuffle(star_positions)
    star_types = {}
    index = 0
    for _ in range(STAR_REVEAL_COUNT):
        star_types[star_positions[index]] = "reveal"
        index += 1
    for _ in range(STAR_SEND_SELF_COUNT):
        star_types[star_positions[index]] = "send_self"
        index += 1
    for _ in range(STAR_SEND_OPP_COUNT):
        star_types[star_positions[index]] = "send_opp"
        index += 1
    for _ in range(STAR_PENALTY_COUNT):
        star_types[star_positions[index]] = "penalty"
        index += 1
    star_positions = set(star_types.keys())
    star_totals = {
        "reveal": STAR_REVEAL_COUNT,
        "send_self": STAR_SEND_SELF_COUNT,
        "send_opp": STAR_SEND_OPP_COUNT,
        "penalty": STAR_PENALTY_COUNT,
    }
    grid_dirty = True
    panel_dirty = True
    used_counts = {"reveal": 0, "send_self": 0, "send_opp": 0, "penalty": 0}

    def update_panel():
        nonlocal used_counts
        remaining_counts = {"reveal": 0, "send_self": 0, "send_opp": 0, "penalty": 0}
        for effect in star_types.values():
            remaining_counts[effect] += 1
        used_counts = {k: star_totals[k] - remaining_counts[k] for k in star_totals}
        render_panel_surface(panel_surface, star_totals, used_counts)

    def ensure_surfaces():
        nonlocal grid_dirty, panel_dirty
        if grid_dirty:
            render_grid_surface(grid_surface, full_grid, human_known, comp_known, start, star_positions)
            grid_dirty = False
        if panel_dirty:
            update_panel()
            panel_dirty = False

    def flash_goal():
        for _ in range(GOAL_FLASH_COUNT):
            ensure_surfaces()
            screen.fill(COLOR_BG)
            screen.blit(panel_surface, (0, 0))
            screen.blit(grid_surface, (PANEL_WIDTH, 0))
            draw_goal(screen, goal, PANEL_WIDTH)
            draw_agent(screen, human_pos, COLOR_HUMAN, PANEL_WIDTH)
            draw_agent(screen, comp_pos, COLOR_COMP, PANEL_WIDTH)
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                (PANEL_WIDTH + MARGIN + goal[1] * (CELL_SIZE + MARGIN) + CELL_SIZE // 2,
                 MARGIN + goal[0] * (CELL_SIZE + MARGIN) + CELL_SIZE // 2),
                CELL_SIZE // 2 + 3,
                2,
            )
            pygame.display.flip()
            pygame.time.delay(GOAL_FLASH_MS)

    def set_status(message):
        nonlocal status_message, status_until_ms
        status_message = message
        status_until_ms = pygame.time.get_ticks() + 3500

    def apply_star_effect(actor, opponent, is_human_actor):
        nonlocal human_score, comp_score, grid_dirty, panel_dirty
        if actor not in star_types:
            return actor, opponent
        effect = star_types.pop(actor)
        star_positions.discard(actor)
        grid_dirty = True
        panel_dirty = True
        if effect == "reveal":
            reveal_box(human_known if is_human_actor else comp_known, full_grid, actor, size=8)
            if not is_human_actor:
                reveal_box(comp_planning, full_grid, actor, size=8)
            set_status("Star: Revealed an 8x8 area.")
        elif effect == "send_self":
            actor = start
            set_status("Star: Sent player back to start.")
        elif effect == "send_opp":
            opponent = start
            set_status("Star: Sent opponent back to start.")
        elif effect == "penalty":
            total_cells = HEIGHT * WIDTH
            count = max(1, int(total_cells * 0.2))
            all_cells = [(r, c) for r in range(HEIGHT) for c in range(WIDTH)]
            random.shuffle(all_cells)
            affected = set(all_cells[:count])
            if human_pos in affected:
                human_score = max(0, human_score - 1)
            if comp_pos in affected:
                comp_score = max(0, comp_score - 1)
            ensure_surfaces()
            flash_cells(
                screen,
                clock,
                grid_surface,
                panel_surface,
                goal,
                human_pos,
                comp_pos,
                affected,
                PANEL_WIDTH,
            )
            set_status("Penalty Zones -1 Point")
        return actor, opponent

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.KEYDOWN and winner is None and turn == "human":
                if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    candidate = next_human_position(event.key, human_pos)
                    r = clamp(candidate[0], 0, HEIGHT - 1)
                    c = clamp(candidate[1], 0, WIDTH - 1)
                    candidate = (r, c)

                    reveal_cell(human_known, full_grid, candidate)
                    if full_grid[r][c] == FREE:
                        human_pos = candidate

                    reveal_neighbors(human_known, full_grid, human_pos)
                    grid_dirty = True
                    if human_pos in star_positions:
                        human_pos, comp_pos = apply_star_effect(human_pos, comp_pos, True)

                    if human_pos == goal:
                        human_score += 1
                        set_status("Human scored a point!")
                        if human_score >= winning_score:
                            winner = "Human"
                        else:
                            goal = find_random_goal(full_grid, human_pos, comp_pos, goal)
                            flash_goal()
                    else:
                        merge_known(comp_known, human_known)
                        merge_known(comp_planning, human_known)
                        grid_dirty = True
                        turn = "computer"

        if winner is None and turn == "computer":
            path, closed_list, g_values, _expanded = adaptive_astar(comp_planning, comp_pos, goal, h_values)
            if path is None or len(path) < 2:
                turn = "human"
            else:
                next_step = path[1]
                if full_grid[next_step[0]][next_step[1]] == BLOCKED:
                    comp_known[next_step[0]][next_step[1]] = BLOCKED
                    comp_planning[next_step[0]][next_step[1]] = BLOCKED
                else:
                    comp_pos = next_step
                    comp_known[comp_pos[0]][comp_pos[1]] = FREE
                    comp_planning[comp_pos[0]][comp_pos[1]] = FREE
                    neighbors = find_all_neighbors(comp_pos)
                    if neighbors and COMP_REVEAL_NEIGHBORS > 0:
                        random.shuffle(neighbors)
                        for nr, nc in neighbors[:COMP_REVEAL_NEIGHBORS]:
                            comp_known[nr][nc] = full_grid[nr][nc]
                            comp_planning[nr][nc] = full_grid[nr][nc]
                    grid_dirty = True
                    if comp_pos in star_positions:
                        comp_pos, human_pos = apply_star_effect(comp_pos, human_pos, False)

                for cell in closed_list:
                    h_values[cell] = g_values[goal] - g_values[cell]

                if comp_pos == goal:
                    comp_score += 1
                    set_status("Computer scored a point!")
                    if comp_score >= winning_score:
                        winner = "Computer"
                    else:
                        goal = find_random_goal(full_grid, human_pos, comp_pos, goal)
                        flash_goal()
                else:
                    merge_known(human_known, comp_known)
                    grid_dirty = True
                    turn = "human"
                pygame.time.delay(COMP_DELAY_MS)

        ensure_surfaces()
        screen.fill(COLOR_BG)
        screen.blit(panel_surface, (0, 0))
        screen.blit(grid_surface, (PANEL_WIDTH, 0))
        draw_goal(screen, goal, PANEL_WIDTH)
        draw_agent(screen, human_pos, COLOR_HUMAN, PANEL_WIDTH)
        draw_agent(screen, comp_pos, COLOR_COMP, PANEL_WIDTH)

        font = pygame.font.SysFont("arial", 20)
        score_text = font.render(f"Human {human_score} - {comp_score} Computer", True, COLOR_SCORE)
        screen.blit(score_text, (12, HEIGHT * CELL_SIZE - 28))

        if status_message and pygame.time.get_ticks() < status_until_ms:
            status_text = font.render(status_message, True, COLOR_STATUS_TEXT)
            text_rect = status_text.get_rect(center=(PANEL_WIDTH + grid_width // 2, grid_height // 2))
            padding_x = 18
            padding_y = 10
            box_rect = pygame.Rect(
                text_rect.left - padding_x,
                text_rect.top - padding_y,
                text_rect.width + padding_x * 2,
                text_rect.height + padding_y * 2,
            )
            pygame.draw.rect(screen, COLOR_STATUS_BG, box_rect, border_radius=6)
            screen.blit(status_text, text_rect)

        if winner is not None:
            font = pygame.font.SysFont("arial", 24)
            text = font.render(f"{winner} wins! Press Esc to quit.", True, COLOR_TEXT)
            screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

        keys = pygame.key.get_pressed()
        if winner is not None and keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit(0)


def main():
    print()
    print("Difficulty: easy / hard")
    difficulty = input("Select difficulty: ").strip().lower()
    if difficulty not in ("easy", "hard"):
        difficulty = "easy"

    difficulty_settings = {
        "easy": {"comp_delay_ms": 200, "comp_reveal_neighbors": 0},
        "hard": {"comp_delay_ms": 200, "comp_reveal_neighbors": 1},
    }
    settings = difficulty_settings[difficulty]
    global COMP_DELAY_MS, COMP_REVEAL_NEIGHBORS
    COMP_DELAY_MS = settings["comp_delay_ms"]
    COMP_REVEAL_NEIGHBORS = settings["comp_reveal_neighbors"]

    use_random = input("Use random maze? y/n ")
    if use_random == "y":
        full_grid, start, goal = random_grid()
    else:
        maze_file_name = input("Maze file name: ")
        full_grid, start, goal = load_grid(maze_file_name)

    run_game(full_grid, start, goal)


if __name__ == '__main__':
    main()
