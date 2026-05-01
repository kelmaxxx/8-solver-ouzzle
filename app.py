from flask import Flask, render_template, request, jsonify
import random
from solver import solve_bfs, solve_dfs, is_solvable, GOAL_STATE

app = Flask(__name__)


def generate_random_puzzle():
    """Generate a random solvable 8-puzzle that isn't already solved."""
    tiles = list(range(9))
    while True:
        random.shuffle(tiles)
        if is_solvable(tiles) and tuple(tiles) != tuple(GOAL_STATE):
            return tiles


@app.route("/")
def index():
    """Serve the main HTML page."""
    return render_template("index.html")


@app.route("/solve", methods=["POST"])
def solve():
    """
    Receive the puzzle from the frontend, solve it with BFS,
    and return the solution steps + all visited states as JSON.
    """
    data = request.get_json()
    start_state = data.get("state")

    if not start_state or len(start_state) != 9:
        return jsonify({"error": "Invalid puzzle state"}), 400

    if sorted(start_state) != list(range(9)):
        return jsonify({"error": "Puzzle must contain numbers 0-8"}), 400

    # Already solved?
    if tuple(start_state) == tuple(GOAL_STATE):
        return jsonify({"already_solved": True, "steps": 0, "moves": 0})

    # Not solvable?
    if not is_solvable(start_state):
        return jsonify({"unsolvable": True})

    # Run BFS
    solution_path, steps_explored, visited_states = solve_bfs(start_state)

    if solution_path is None:
        return jsonify({"unsolvable": True})

    return jsonify({
        "success":         True,
        "solution":        solution_path,               # Step-by-step solution
        "total_moves":     len(solution_path),          # Moves in solution
        "steps_explored":  steps_explored,              # BFS nodes processed
        "visited_states":  [list(s) for s in visited_states],  # ALL visited states
        "total_visited":   len(visited_states),         # Count of visited states
        "algorithm":       "Breadth-First Search (BFS)"
    })


@app.route("/solve_dfs", methods=["POST"])
def solve_dfs_route():
    """
    Receive the puzzle from the frontend, solve it with DFS,
    and return the solution steps + all visited states as JSON.
    """
    data = request.get_json()
    start_state = data.get("state")

    if not start_state or len(start_state) != 9:
        return jsonify({"error": "Invalid puzzle state"}), 400

    if sorted(start_state) != list(range(9)):
        return jsonify({"error": "Puzzle must contain numbers 0-8"}), 400

    # Already solved?
    if tuple(start_state) == tuple(GOAL_STATE):
        return jsonify({"already_solved": True, "steps": 0, "moves": 0})

    # Not solvable?
    if not is_solvable(start_state):
        return jsonify({"unsolvable": True})

    # Run DFS
    solution_path, steps_explored, visited_states = solve_dfs(start_state)

    if solution_path is None:
        return jsonify({"unsolvable": True})

    return jsonify({
        "success":        True,
        "solution":       solution_path,
        "total_moves":    len(solution_path),          # Path cost (may be non-optimal)
        "steps_explored": steps_explored,              # DFS nodes processed
        "visited_states": [list(s) for s in visited_states],
        "total_visited":  len(visited_states),
        "algorithm":      "Depth-First Search (DFS)"
    })


@app.route("/random", methods=["GET"])
def random_puzzle():
    """Generate and return a random solvable puzzle."""
    puzzle = generate_random_puzzle()
    return jsonify({"state": puzzle})


if __name__ == "__main__":
    print("=" * 50)
    print("  8-Puzzle Solver is running!")
    print("  Open your browser: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)
