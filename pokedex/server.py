from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from treys import Card, Deck
from enum import Enum

# Assuming these classes are defined in your project
from src.poker import Poker, Round, GameStage
from src.player import Player, Action
from src.hand import Hand
from flask_cors import CORS

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'poker-secret'
# socketio = SocketIO(app, cors_allowed_origins="*")
# CORS(app)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173"]  # Svelte default dev server port
    }
})

# Game state (preset for prototyping)
game = None

@app.route('/start_game', methods=['GET'])
def start_game():
    global game

    # Define three players with preset names and stacks
    players = [
        Player("Harry Potter", 1000),
        Player("Cho Chang", 750),
        Player("Luna Lovegood", 200),
        # Player("Ron Weasley"),
    ]
    
    # Initialize a poker game with small blind of 10
    poker = Poker(players=players, small_blind=10)
    # poker.set_stacks(1000)
    
    # Deal cards and setup the round
    round = poker.new_round()
    round.deal()
    round.post_blinds()

    game = poker
    # Prepare the game state to return
    game_state = round.to_dict()

    # Save the game for later interactions

    return jsonify(game_state)

@app.route('/next_round', methods=['POST'])
def next_round():
    global game
    
    # Deal cards and setup the round
    round = game.new_round()
    round.deal()
    round.post_blinds()

    # Prepare the game state to return
    game_state = round.to_dict()


    return jsonify(game_state)


@app.route('/next_turn', methods=['POST'])
def next_turn():
    global game
    round = game.round

    # Get the current player

    # Get the action from the request
    action = request.json["action"]
    player_name = request.json["player_name"]

    # player verification

    action = Action.dict_to_action(action)

    # Perform the action
    round.player_action(action)

    # Prepare the game state to return
    game_state = round.to_dict()

    if round.betting_round_over():
        players, hand, rank = round.reveal()
        game_state["winner"] = {
            "players": [player.to_dict() for player in players],
            "hand": Hand.ints_to_str(hand) if hand else None,
            "rank": rank
        }

        round.distribute_winnings(players)


    return jsonify(game_state)

if __name__ == '__main__':
    # socketio.run(app, debug=True)
    app.run(debug=True)