from collections import deque

# The goal state of the 8-puzzle
GOAL_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 0)

# Possible moves: (row_change, col_change, direction_name)
MOVES = [
    (-1, 0, "Up"),
    (1, 0, "Down"),
    (0, -1, "Left"),
    (0, 1, "Right"),
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
            # Convert state tuple to a list so we can swap
            new_state = list(state)

            # Swap the blank (0) with the neighbor tile
            blank_index = row * 3 + col
            neighbor_index = new_row * 3 + new_col
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
    An inversion is when a larger number appears before a smaller number.
    """
    tiles = [x for x in state if x != 0]  # Remove the blank
    inversions = 0

    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1

    return inversions % 2 == 0


def solve_bfs(start_state):
    """
    Solve the 8-puzzle using Breadth-First Search (BFS).

    BFS explores all states level by level (by number of moves).
    It guarantees finding the SHORTEST solution path.

    Returns:
        - solution_path: list of (state, move) tuples showing each step
        - steps_explored: total number of states we looked at
    """
    start_state = tuple(start_state)

    # Check if already solved
    if start_state == GOAL_STATE:
        return [], 0

    # Check if the puzzle can even be solved
    if not is_solvable(start_state):
        return None, 0

    # Queue holds: (current_state, path_taken_so_far)
    queue = deque()
    queue.append((start_state, []))

    # Keep track of visited states so we don't revisit them
    visited = set()
    visited.add(start_state)

    steps_explored = 0

    while queue:
        current_state, path = queue.popleft()
        steps_explored += 1

        for next_state, direction in get_neighbors(current_state):
            if next_state == GOAL_STATE:
                # Found the solution! Return the complete path
                solution_path = path + [(next_state, direction)]
                return solution_path, steps_explored

            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [(next_state, direction)]))

    # No solution found (shouldn't happen if is_solvable() returned True)
    return None, steps_explored
