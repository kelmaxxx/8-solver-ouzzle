from collections import deque
import heapq

# The goal state of the 8-puzzle (0 = blank tile)
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Possible moves: (row_change, col_change, direction_name)
MOVES = [
    (-1, 0, "Up"),
    (1,  0, "Down"),
    (0, -1, "Left"),
    (0,  1, "Right"),
]


def get_blank_position(state):
    """Find where the blank tile (0) is in the puzzle."""
    index = state.index(0)
    row = index // 3
    col = index % 3
    return row, col


def get_neighbors(state):
    """
    Return all valid states reachable from the current state
    by sliding one tile into the blank space.
    """
    neighbors = []
    row, col = get_blank_position(state)

    for dr, dc, direction in MOVES:
        new_row = row + dr
        new_col = col + dc

        # Check if the new position is within the 3x3 grid
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_state = list(state)

            blank_index = row * 3 + col
            neighbor_index = new_row * 3 + new_col

            # Swap the blank with the neighbor tile
            new_state[blank_index], new_state[neighbor_index] = (
                new_state[neighbor_index],
                new_state[blank_index],
            )
            neighbors.append((tuple(new_state), direction))

    return neighbors


def is_solvable(state):
    """
    Check if the puzzle can be solved.
    A puzzle is solvable if the number of inversions is even.
    An inversion = a larger number appearing before a smaller number.
    """
    tiles = [x for x in state if x != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions % 2 == 0


def manhattan_distance(state):
    """
    Heuristic: sum of Manhattan distances of each tile from its goal position.

    For each tile (except blank), calculate how many rows + columns
    away it is from where it should be in the goal state.
    A lower value means the puzzle is closer to the goal.
    """
    distance = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue                        # ignore the blank tile
        goal_index = GOAL_STATE.index(tile) # where this tile should be
        cur_row,  cur_col  = i // 3,          i % 3
        goal_row, goal_col = goal_index // 3, goal_index % 3
        distance += abs(cur_row - goal_row) + abs(cur_col - goal_col)
    return distance


def solve_best_first(start_state):
    """
    Solve the 8-puzzle using Greedy Best-First Search.

    Uses Manhattan distance as the heuristic h(n).
    Always expands the node that LOOKS closest to the goal (lowest h).
    Informed search — much faster than BFS/DFS on average, but does
    NOT guarantee the shortest path (greedy, not optimal).

    Priority queue entry: (h(n), tie_breaker, state, path)

    Returns:
        - solution_path : list of {state, move} dicts for the solution
        - steps_explored: total number of states popped/processed
        - visited_states : ordered list of ALL states visited during search
    """
    start_state = tuple(start_state)

    # Already solved?
    if start_state == GOAL_STATE:
        return [], 0, [start_state]

    # Not solvable?
    if not is_solvable(start_state):
        return None, 0, []

    h_start = manhattan_distance(start_state)

    # Min-heap: (heuristic, counter, state, path)
    # Counter breaks ties so Python never compares states directly
    counter = 0
    heap = [(h_start, counter, start_state, [])]

    # visited set — prevents re-expanding states
    visited = set()
    visited.add(start_state)

    # Ordered list of visited states (for display)
    visited_order = [start_state]

    steps_explored = 0

    while heap:
        h, _, current_state, path = heapq.heappop(heap)
        steps_explored += 1

        for next_state, direction in get_neighbors(current_state):
            if next_state == GOAL_STATE:
                visited_order.append(next_state)
                solution_path = path + [{"state": list(next_state), "move": direction}]
                return solution_path, steps_explored, visited_order

            if next_state not in visited:
                visited.add(next_state)
                visited_order.append(next_state)
                counter += 1
                h_next = manhattan_distance(next_state)
                heapq.heappush(heap, (
                    h_next, counter, next_state,
                    path + [{"state": list(next_state), "move": direction}]
                ))

    return None, steps_explored, visited_order


def solve_astar(start_state):
    """
    Solve the 8-puzzle using A* Search.

    A* combines:
        g(n) = actual cost to reach node n from the start (number of moves so far)
        h(n) = Manhattan distance heuristic (estimated cost to goal)
        f(n) = g(n) + h(n)  ← priority used in the heap

    Always expands the node with the lowest f(n).
    Because Manhattan distance is ADMISSIBLE (never overestimates),
    A* is guaranteed to find the SHORTEST solution — just like BFS
    but much faster because the heuristic guides the search.

    Priority queue entry: (f(n), tie_breaker, g(n), state, path)

    Returns:
        - solution_path : list of {state, move} dicts for the solution
        - steps_explored: total number of states popped/processed
        - visited_states : ordered list of ALL states visited during search
    """
    start_state = tuple(start_state)

    # Already solved?
    if start_state == GOAL_STATE:
        return [], 0, [start_state]

    # Not solvable?
    if not is_solvable(start_state):
        return None, 0, []

    g_start = 0
    h_start = manhattan_distance(start_state)
    f_start = g_start + h_start

    # Min-heap: (f, counter, g, state, path)
    counter = 0
    heap = [(f_start, counter, g_start, start_state, [])]

    # visited set — once a state is expanded via the cheapest path, skip it
    visited = set()
    visited.add(start_state)

    # Ordered list of visited states (for display)
    visited_order = [start_state]

    steps_explored = 0

    while heap:
        f, _, g, current_state, path = heapq.heappop(heap)
        steps_explored += 1

        for next_state, direction in get_neighbors(current_state):
            if next_state == GOAL_STATE:
                visited_order.append(next_state)
                solution_path = path + [{"state": list(next_state), "move": direction}]
                return solution_path, steps_explored, visited_order

            if next_state not in visited:
                visited.add(next_state)
                visited_order.append(next_state)
                g_next = g + 1                          # each move costs 1
                h_next = manhattan_distance(next_state)
                f_next = g_next + h_next
                counter += 1
                heapq.heappush(heap, (
                    f_next, counter, g_next, next_state,
                    path + [{"state": list(next_state), "move": direction}]
                ))

    return None, steps_explored, visited_order


def solve_dfs(start_state):
    """
    Solve the 8-puzzle using Depth-First Search (DFS).

    DFS explores as deep as possible along each branch before backtracking.
    It does NOT guarantee the shortest solution — the path found can be
    much longer than optimal. Uses a visited set to avoid infinite loops.

    Returns:
        - solution_path : list of {state, move} dicts for the solution
        - steps_explored: total number of states popped/processed
        - visited_states : ordered list of ALL states visited during search
    """
    start_state = tuple(start_state)

    # Already solved?
    if start_state == GOAL_STATE:
        return [], 0, [start_state]

    # Not solvable?
    if not is_solvable(start_state):
        return None, 0, []

    # Stack holds: (current_state, path_taken_so_far)
    # Using a list as a stack — append to push, pop() to pull from top
    stack = [(start_state, [])]

    # visited set — prevents revisiting states and infinite loops
    visited = set()
    visited.add(start_state)

    # Ordered list of visited states (for display)
    visited_order = [start_state]

    steps_explored = 0

    while stack:
        current_state, path = stack.pop()   # pop from top (LIFO)
        steps_explored += 1

        for next_state, direction in get_neighbors(current_state):
            if next_state == GOAL_STATE:
                visited_order.append(next_state)
                solution_path = path + [{"state": list(next_state), "move": direction}]
                return solution_path, steps_explored, visited_order

            if next_state not in visited:
                visited.add(next_state)
                visited_order.append(next_state)
                stack.append((next_state, path + [{"state": list(next_state), "move": direction}]))

    return None, steps_explored, visited_order


def solve_bfs(start_state):
    """
    Solve the 8-puzzle using Breadth-First Search (BFS).

    BFS explores all states level by level (by number of moves).
    It guarantees finding the SHORTEST solution path.

    Returns:
        - solution_path : list of {state, move} dicts for the solution
        - steps_explored: total number of states dequeued/processed
        - visited_states : ordered list of ALL states visited during search
    """
    start_state = tuple(start_state)

    # Already solved?
    if start_state == GOAL_STATE:
        return [], 0, [start_state]

    # Not solvable?
    if not is_solvable(start_state):
        return None, 0, []

    # Queue holds: (current_state, path_taken_so_far)
    queue = deque()
    queue.append((start_state, []))

    # visited set — prevents revisiting states
    visited = set()
    visited.add(start_state)

    # Ordered list of visited states (for display — requirement #4)
    visited_order = [start_state]

    steps_explored = 0

    while queue:
        current_state, path = queue.popleft()
        steps_explored += 1

        for next_state, direction in get_neighbors(current_state):
            if next_state == GOAL_STATE:
                # Add goal to visited list
                visited_order.append(next_state)

                solution_path = path + [{"state": list(next_state), "move": direction}]
                return solution_path, steps_explored, visited_order

            if next_state not in visited:
                visited.add(next_state)
                visited_order.append(next_state)
                queue.append((next_state, path + [{"state": list(next_state), "move": direction}]))

    return None, steps_explored, visited_order
