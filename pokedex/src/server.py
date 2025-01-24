from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from poker import Poker, Round, Player  # Import your game classes

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

games = {}  # Dictionary to manage ongoing games by room ID

@app.route("/create_game", methods=["POST"])
def create_game():
    data = request.json
    room_id = data.get("room_id")
    small_blind = data.get("small_blind", 10)

    # Initialize the game
    poker = Poker(small_blind=small_blind)
    games[room_id] = poker
    return jsonify({"message": "Game created", "room_id": room_id})

@app.route("/join_game", methods=["POST"])
def join_game():
    data = request.json
    room_id = data["room_id"]
    player_name = data["player_name"]
    stack = data.get("stack", 100)

    game = games.get(room_id)
    if not game:
        return jsonify({"error": "Game not found"}), 404

    player = Player(name=player_name, stack=stack)
    game.add_player(player)
    return jsonify({"message": f"{player_name} joined the game"})

@socketio.on("start_round")
def start_round(data):
    room_id = data["room_id"]
    game = games.get(room_id)

    if not game:
        emit("error", {"error": "Game not found"})
        return

    round_instance = game.new_round()
    games[room_id].current_round = round_instance

    emit("round_started", round_instance.get_game_state(), broadcast=True)

@socketio.on("player_action")
def player_action(data):
    room_id = data["room_id"]
    player_id = data["player_id"]
    action = data["action"]
    amount = data.get("amount", 0)

    game = games.get(room_id)
    if not game or not game.current_round:
        emit("error", {"error": "Game or round not found"})
        return

    try:
        game.current_round.process_action(player_id, action, amount)
        emit("game_update", game.current_round.get_game_state(), broadcast=True)
    except ValueError as e:
        emit("error", {"error": str(e)})

if __name__ == "__main__":
    socketio.run(app, debug=True)
