
from src.poker import Poker, GameStage
from src.player import Player, Action


players = [
    Player("Harry Potter", 1000),
    Player("Cho Chang", 1000),
    Player("Luna Lovegood", 75),
    Player("Ron Weasley", 1000)
]

poker = Poker(players=players, small_blind=10)

round = poker.new_round()
round.deal()
round.set_stage(GameStage.FLOP)

current_player = round.get_current_player() 
round.player_action(current_player.name, Action.bet(100))

current_player = round.get_current_player()
round.player_action(current_player.name, Action.call())

current_player = round.get_current_player() 
round.player_action(current_player.name, Action.call())

current_player = round.get_current_player()
round.player_action(current_player.name, Action.raise_bet(200))

print(round)
print(round.str_actions())
