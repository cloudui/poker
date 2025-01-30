from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from treys import Card, Deck
from enum import Enum

# Assuming these classes are defined in your project
from src.poker import Poker, Round, GameStage
from src.player import Player
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

def get_turn():
    global game

    # Get the current player
    player, actions = game["round"].get_current_player_and_actions()

    # Prepare the game state to return
    turn = {
        "player": {
            "name": player.name,
            "stack": player.stack,
            "hand": player.str_hand()
        },
        "actions": [action.to_dict() for action in actions],
    }

    return turn

@app.route('/start_game', methods=['GET'])
def start_game():
    global game

    # Define three players with preset names and stacks
    players = [
        Player(name="Harry Potter"),
        Player(name="Cho Chang"),
        Player(name="Luna Lovegood")
    ]
    
    # Initialize a poker game with small blind of 10
    poker = Poker(players=players, small_blind=10)
    poker.set_stacks(1000)
    
    # Deal cards and setup the round
    round = poker.new_round()
    round.deal()
    round.post_blinds()

    game = {
        "poker": poker,
        "round": round
    }
    # Prepare the game state to return
    game_state = {
        "players": [
            {
                "name": player.name,
                "stack": player.stack,
                "hand": player.str_hand()
            } for player in round.players
        ],
        "stage": round.stage.name,
        "pot": {
            "amount": round.pot.amount,
        },
        "small_blind_player": round.small_blind_player.name,
        "big_blind_player": round.big_blind_player.name,
        "turn": get_turn()
    }

    # Save the game for later interactions

    return jsonify(game_state)



if __name__ == '__main__':
    # socketio.run(app, debug=True)
    app.run(debug=True)