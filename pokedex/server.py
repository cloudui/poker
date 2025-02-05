from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from treys import Card, Deck
from enum import Enum
import json

# Assuming these classes are defined in your project
from src.poker import Poker, Round, GameStage
from src.player import Player, Action
from src.hand import Hand

app = FastAPI()

# Allow CORS for frontend (Svelte running on port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Game state
game = None
active_connections = {}  # {player_name: WebSocket}


class PlayerAction(BaseModel):
    player_name: str
    action: dict  # Action should be passed as a dict


@app.post("/start_game")
async def start_game():
    """Starts a new poker game."""
    global game

    players = [
        Player("Tyson the Conqueror", 1000),
        Player("Lord Voldemort", 1000),
        Player("Cho Chang", 250),
        Player("Luna Lovegood", 320),
    ]
    
    poker = Poker(players=players, small_blind=10)
    round = poker.new_round()
    round.deal()
    round.post_blinds()

    game = poker
    game_state = round.to_dict()

    return game_state


@app.post("/next_round")
async def next_round():
    """Moves to the next round in the game."""
    global game
    
    round = game.new_round()
    round.deal()
    round.post_blinds()

    game_state = round.to_dict()
    return game_state


@app.post("/next_turn")
async def next_turn(action_data: PlayerAction):
    """Processes a player's action and updates the game state."""
    global game
    round = game.round

    action = Action.dict_to_action(action_data.action)

    round.player_action(action)
    game_state = round.to_dict()

    if round.betting_round_over():
        players, hand, rank = round.reveal()
        game_state["winner"] = {
            "players": [player.to_dict() for player in players],
            "hand": Hand.ints_to_str(hand),
            "rank": rank
        }
        round.distribute_winnings()

    # Broadcast update to all players
    await broadcast_game_state(game_state)

    return game_state


@app.websocket("/ws/{player_name}")
async def websocket_endpoint(websocket: WebSocket, player_name: str):
    """Handles WebSocket connections for real-time updates."""
    await websocket.accept()
    active_connections[player_name] = websocket

    try:
        while True:
            # Receive action from player
            data = await websocket.receive_text()
            action_data = json.loads(data)

            print(f"Received action from {player_name}: {action_data}")  # Debug log

            # Validate action format
            if "action" not in action_data or "player_name" not in action_data:
                continue

            player_name = action_data["player_name"]
            action_dict = action_data["action"]

            if game:
                round = game.round
                action = Action.dict_to_action(action_dict)
                
                # Process the player's action
                round.player_action(action)
                game_state = round.to_dict()

                # Check if betting round is over
                if round.betting_round_over():
                    players, hand, rank = round.reveal()
                    game_state["winner"] = {
                        "players": [player.to_dict() for player in players],
                        "hand": Hand.ints_to_str(hand),
                        "rank": rank
                    }
                    round.distribute_winnings()

                # Broadcast updated game state to all players
                await broadcast_game_state(game_state)

    except WebSocketDisconnect:
        del active_connections[player_name]
        print(f"Player {player_name} disconnected")



async def broadcast_game_state(game_state):
    """Sends the updated game state to all connected players."""
    message = json.dumps(game_state)
    for player, ws in active_connections.items():
        try:
            await ws.send_text(message)
        except:
            pass  # Handle disconnected players silently

