import random
from enum import Enum
from treys import Card, Deck

from .hand import HandEvaluator

from .player import Player


class GameStage(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    ROUND_OVER = 4

class Pot:
    def __init__(self, minimum_bet=0):
        self.amount = 0
        self.side_pots = []
        self.last_raise = (None, 0)
        self.min_raise_amount = minimum_bet
        self.betting_began = False

    def add(self, amount):
        self.amount += amount
    
    def set_last_raise(self, player, amount):
        self.min_raise_amount = amount - self.last_raise[1]
        self.last_raise = (player, amount)
    
    def get_last_raise(self):
        return self.last_raise
    
    def get_minimum_raise(self):
        return self.min_raise_amount + self.last_raise[1]

    def get_minimum_bet(self):
        return self.last_raise[1]

    def next_round(self):
        self.last_raise = (None, 0)
        self.min_raise_amount = 0


    def reset(self):
        self.amount = 0
        self.side_pots = []
        self.last_raise = (None, 0)
        self.min_raise_amount = 0
    
    def distribute_winnings(self, players):
        for player in players:
            player.win(self.amount)
        
        self.reset()

class Round:
    def __init__(self, players: list[Player], small_blind, small_blind_index=0):
        self.pot = Pot(small_blind*2)
        self.deck = Deck()
        self.board = []
        self.small_blind = small_blind
        self.big_blind = small_blind * 2
        self.stage = GameStage.PREFLOP
        self.evaluator = HandEvaluator()
        
        self.players = [player for player in players[small_blind_index:] + players[:small_blind_index]]

    def start_betting_round(self):
        if self.stage == GameStage.ROUND_OVER:
            raise ValueError("Round is over")

        self._bets()
        if self.stage == GameStage.ROUND_OVER:
            print("Round is over.")
            return

        self.stage = GameStage(self.stage.value + 1)
        if self.stage == GameStage.FLOP:
            self.board += self.deck.draw(3)
        elif self.stage == GameStage.TURN:
            self.board += self.deck.draw(1)        
        elif self.stage == GameStage.RIVER:
            self.board += self.deck.draw(1)

        self.pot.reset()
        
    def _bets(self):
        i = 0
        
        if self.stage == GameStage.PREFLOP:
            i = 2 if len(self.players) > 2 else 0
            sb = self.players[0]
            bb = self.players[1]
            
            print(f"Small blind: {sb.name} auto-bets {self.small_blind}")
            print(f"Big blind: {bb.name} auto-bets {self.big_blind}")

            sb.bet(self.small_blind)
            bb.bet(self.big_blind)

            self.pot.set_last_raise(bb, self.big_blind)
            print()

        while True:
            if len(self.players) == 1:
                print("All other players have folded")
                self.stage = GameStage.ROUND_OVER
                break

            player = self.players[i]

            player_last_bet = player.current_round_bet()
            amount_to_call = self.pot.last_raise[1] - player_last_bet

            last_player_raise, _ = self.pot.get_last_raise()
            
            if last_player_raise == player:
                print("All players have called")
                break
            if i == 0 and not self.pot.betting_began:
                print("All players have checked")
                break

            print(f"Player {player}")
            print(f"Minimum raise: {self.pot.get_minimum_raise()}")
            if amount_to_call > 0:
                print(f"Amount to call: {amount_to_call}")


            action_input = input(f"{player.name}: ")
            action_input = action_input.lower().strip().split()

            action = action_input[0]
            amount = int(action_input[1]) if len(action_input) > 1 else 0

            if action == "fold":
                player.fold()
            elif action == "call":
                player.bet(amount_to_call)
            elif action == "raise":
                player.bet(amount)
                self.pot.set_last_raise(player, amount)
            
            i += 1
            if i == len(self.players):
                i = 0
                self.players = [player for player in self.players if not player.folded()]
            
            print()


    def deal(self):
        for player in self.players:
            player.set_cards(self.deck.draw(2))

    def reveal(self):
        if self.stage != GameStage.ROUND_OVER:
            raise ValueError("Cannot reveal cards before the river")
        
        winner = []
        best_ev = 10_000

        for player in self.players:
            hand, rank, ev = self.evaluator.best_hand_rank_eval(player.hand(), self.board)
            print(f"{player.name:<15} {rank:<15} {Card.ints_to_pretty_str(hand)}")

            if ev < best_ev:
                best_ev = ev
                winner = [player]
            elif ev == best_ev:
                winner.append(player)
        
        print(f"Winner: {', '.join([player.name for player in winner])}")
    
    def __repr__(self):
        res = f"Stage: {self.stage.name.capitalize()}\n"
        res += f"Board: {Card.ints_to_pretty_str(self.board)}\n\n"
        for player in self.players:
            res += f'{str(player)}\n'
        
        return res
    

class Poker:
    def __init__(self, players: list[Player]=[], small_blind=10):
        self.players = players
        self.small_blind = small_blind
        self.big_blind = 2*small_blind

    def setup_game(self, players, small_blind):
        self.players = players
        self.set_small_blind(small_blind)

    def set_small_blind(self, small_blind):
        self.small_blind = small_blind
        self.big_blind = 2*small_blind

    def add_player_by_name(self, name: str, stack=0):
        self.players.append(Player(name, stack))
    
    def add_player(self, player: Player):
        self.players.append(player)
    
    def set_stacks(self, amount):
        for player in self.players:
            player.set_stack(amount)
    
    def new_round(self):
        return Round(self.players, self.small_blind)
