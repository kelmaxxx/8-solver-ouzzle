from flask import Flask, render_template, request, jsonify
import random
from solver import solve_bfs, is_solvable, GOAL_STATE

app = Flask(__name__)


def generate_random_puzzle():
    """
    Generate a random solvable 8-puzzle configuration.
    Keep shuffling until we get one that's solvable.
    """
    tiles = list(range(9))  # [0, 1, 2, 3, 4, 5, 6, 7, 8]
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
    and return the solution steps as JSON.
    """
    data = request.get_json()
    start_state = data.get("state")

    if not start_state or len(start_state) != 9:
        return jsonify({"error": "Invalid puzzle state"}), 400

    # Check all numbers 0-8 are present
    if sorted(start_state) != list(range(9)):
        return jsonify({"error": "Puzzle must contain numbers 0-8"}), 400

    # Check if already solved
    if tuple(start_state) == tuple(GOAL_STATE):
        return jsonify({"already_solved": True, "steps": 0, "moves": 0})

    # Check if solvable
    if not is_solvable(start_state):
        return jsonify({"unsolvable": True})

    # Run BFS solver
    solution_path, steps_explored = solve_bfs(start_state)

    if solution_path is None:
        return jsonify({"unsolvable": True})

    # Format the solution for the frontend
    # Each step contains the board state and the move made
    formatted_steps = []
    for state, move in solution_path:
        formatted_steps.append({
            "state": list(state),
            "move": move
        })

    return jsonify({
        "success": True,
        "solution": formatted_steps,
        "total_moves": len(solution_path),       # How many tile moves to solve
        "steps_explored": steps_explored,         # How many states BFS visited
        "algorithm": "Breadth-First Search (BFS)"
    })


@app.route("/random", methods=["GET"])
def random_puzzle():
    """Generate and return a random solvable puzzle."""
    puzzle = generate_random_puzzle()
    return jsonify({"state": puzzle})


if __name__ == "__main__":
    print("=" * 50)
    print("  8-Puzzle Solver is running!")
    print("  Open your browser and go to:")
    print("  http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True)