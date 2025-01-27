import random
from enum import Enum
from treys import Card, Deck

from .hand import HandEvaluator

from .player import Player, Action


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
        self.last_bet_raise = (None, 0)
        self.min_raise_amount = minimum_bet
        self.betting_started = False
        self.current_round_bet = 0
        self.minimum_bet = minimum_bet

    def add(self, amount):
        self.amount += amount
        self.current_round_bet += amount
        self.betting_started = True
    
    def set_last_bet_raise(self, player, amount):
        raise_amount = amount - self.last_bet_raise[1]
        if raise_amount < self.min_raise_amount:
            raise ValueError("Raise amount is less than minimum raise")
        
        self.min_raise_amount = amount - self.last_bet_raise[1]
        self.last_bet_raise = (player, amount)
    
    def get_last_bet_raise(self):
        return self.last_bet_raise
    
    def get_minimum_raise(self):
        return self.min_raise_amount + self.last_bet_raise[1]

    def call_amount(self):
        return self.last_bet_raise[1]

    def next_stage(self):
        self.last_bet_raise = (None, 0)
        self.min_raise_amount = 0
        self.betting_started = False
        self.current_round_bet = 0

    def reset(self):
        self.amount = 0
        self.side_pots = []
        self.last_raise = (None, 0)
        self.min_raise_amount = 0
        self.betting_started = False
        self.current_round_bet = 0
    
    def distribute_winnings(self, players):
        n = len(players) 
        split = self.amount // n

        for player in players:
            player.win(split)
        
        self.reset()
    
    def round_stats_str(self):
        return f"Current round total: {self.current_round_bet}\nPot Total: {self.amount}"

    def __repr__(self):
        return f"Pot: {self.amount}"

class Round:
    # type definitions
    pot: Pot
    players: list[Player]
    deck: Deck
    board: list[int]
    small_blind: int
    big_blind: int
    stage: GameStage
    evaluator: HandEvaluator
    small_blind_player: Player
    big_blind_player: Player

    def __init__(self, players: list[Player], small_blind, small_blind_index=0):
        self.pot = Pot(small_blind*2)
        self.deck = Deck()
        self.board = []
        self.small_blind = small_blind
        self.big_blind = small_blind * 2
        self.stage = GameStage.PREFLOP
        self.evaluator = HandEvaluator()

        self.players = [player for player in players[small_blind_index:] + players[:small_blind_index]]
        self.small_blind_player = self.players[0]
        self.big_blind_player = self.players[1]

    def start_betting_round(self):
        if self.stage == GameStage.ROUND_OVER:
            raise ValueError("Round is over")

        # start betting 
        self._bets()

        if self.stage == GameStage.ROUND_OVER:
            print("Round is over.")
            return

        self._next_stage()

        
    def _bets(self):
        i = 0
        player_count = len(self.players)
        
        if self.stage == GameStage.PREFLOP:
            i = 2 if len(self.players) > 2 else 0
            sb = self.small_blind_player
            bb = self.big_blind_player
            
            print(f"Small blind: {sb.name} auto-bets {self.small_blind}")
            print(f"Big blind: {bb.name} auto-bets {self.big_blind}")

            self._post_blinds(sb, bb)
            print()

        while True:
            if len(self.players) == 1 or player_count == 1:
                self.players = [player for player in self.players if not player.folded()]
                print("All other players have folded")
                self.stage = GameStage.ROUND_OVER
                break

            player = self.players[i]

            player_last_bet = player.current_round_bet()
            amount_to_call = player.amount_to_call(self.pot.call_amount())

            last_player_raise, raise_amount = self.pot.get_last_bet_raise()
            
            if not (player == self.big_blind_player and self.stage == GameStage.PREFLOP) and last_player_raise == player:
                print("All players have called")
                break
            if i == 0 and not self.pot.betting_started and player.last_action() == Action.CHECK:
                print("All players have checked")
                break

            print(self.pot.round_stats_str())
            print(f"Player {player}")
            if not self.pot.betting_started:
                print(f"Minimum bet: {self.pot.minimum_bet}.")
            else:
                if amount_to_call > 0:
                    print(f"Amount to call: {amount_to_call} (current bet: {player_last_bet})")
                elif player == self.big_blind_player and self.stage == GameStage.PREFLOP and amount_to_call == 0:
                    print(f"Big blind can check to see the flop.")
                print(f"Minimum raise: {self.pot.get_minimum_raise()} (current bet: {player_last_bet})")

            action_input = input(f"{player.name}: ")
            action_input = action_input.lower().strip().split()

            action = action_input[0]
            amount = int(action_input[1]) if len(action_input) > 1 else 0

            if action == "bet":
                self._bet(player, amount)
            elif action == "fold":
                self._fold(player)
                player_count -= 1
            elif action == "call":
                self._call(player)
            elif action == "raise":
                self._raise(player, amount)
            elif action == "check":
                if self.stage == GameStage.PREFLOP and player == self.big_blind_player and amount_to_call == 0:
                    break
                self._check(player)
            else:
                print("Invalid action. Try again.")
                continue
            
            i += 1
            if i == len(self.players):
                i = 0
                self.players = [player for player in self.players if not player.folded()]
            
            print()

    def _bet(self, player: Player, amount):
        if amount > player.stack:
            raise ValueError("Bet exceeds player's available chips")
        player.bet(amount)
        self.pot.add(amount)

        self.pot.set_last_bet_raise(player, amount)

    def _post_blinds(self, sb: Player, bb: Player):
        sb.post_small_blind(self.small_blind)
        bb.post_big_blind(self.big_blind)

        self.pot.set_last_bet_raise(bb, self.big_blind)

        self.pot.add(self.small_blind)
        self.pot.add(self.big_blind)

    def _raise(self, player: Player, amount):
        if amount < self.pot.get_minimum_raise():
            raise ValueError("Raise amount is less than minimum raise")
        
        amount_raised = player.raise_bet(amount)
        self.pot.set_last_bet_raise(player, amount)
        self.pot.add(amount_raised)
    
    def _call(self, player: Player):
        call_amount = self.pot.call_amount()
        amount_to_call = player.call(call_amount)
        self.pot.add(amount_to_call)
    
    def _fold(self, player: Player):
        player.fold()
    
    def _check(self, player: Player):
        player.check()

    def deal(self):
        for player in self.players:
            player.set_cards(self.deck.draw(2))

    def _next_stage(self):
        for player in self.players:
            player.next_stage()
        
        self.pot.next_stage()

        self.stage = GameStage(self.stage.value + 1)
        if self.stage == GameStage.FLOP:
            self.board += self.deck.draw(3)
        elif self.stage == GameStage.TURN:
            self.board += self.deck.draw(1)        
        elif self.stage == GameStage.RIVER:
            self.board += self.deck.draw(1)

    def betting_round_over(self):
        return self.stage == GameStage.ROUND_OVER
    
    def reveal(self):
        if not self.betting_round_over():
            raise ValueError("Cannot reveal cards before the river")
    
        if len(self.board) < 5:
            print(f"Winner\n{self.players[0]}")
            return
        
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
        self.round = None

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
        if not self.players or len(self.players) < 2:
            raise ValueError("Not enough players to start a round")

        new_round =  Round(self.players, self.small_blind)
        self.round = new_round

        return new_round
