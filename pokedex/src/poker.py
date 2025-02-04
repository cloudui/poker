import random
from enum import Enum
from treys import Card, Deck

from .hand import HandEvaluator

from .player import Player, Action
from .pot import Pot


class GameStage(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    ROUND_OVER = 4

class RoundAction:
    player: Player
    action: Action

    def __init__(self, player, action):
        self.player = player
        self.action = action

    def __repr__(self):
        return f"{self.player.name}: {self.action}"

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

    round_actions: dict[GameStage, list[RoundAction]]
    action_complete_players: set[Player]

    def __init__(self, players: list[Player], small_blind):
        self.pot = Pot(small_blind*2)
        self.deck = Deck()
        self.board = []
        self.small_blind = small_blind
        self.big_blind = small_blind * 2
        self.stage = GameStage.PREFLOP
        self.evaluator = HandEvaluator()

        self.players = players
        self.small_blind_player = self.players[0]
        self.big_blind_player = self.players[1]
        self.player_index = 0

        self._current_bet_round_all_ins = {}
        self.round_actions = {
            GameStage.PREFLOP: [],
            GameStage.FLOP: [],
            GameStage.TURN: [],
            GameStage.RIVER: []
        }

        self.action_complete_players = set()

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

            self.post_blinds()
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
        player.bet(amount)
        all_in = self.pot.add(player, amount)

        self.pot.set_last_bet_raise(player, amount)

        if all_in:
            self.pot.split_pot()

    def post_blinds(self):
        sb = self.small_blind_player
        bb = self.big_blind_player

        sb.post_small_blind(self.small_blind)
        bb.post_big_blind(self.big_blind)

        self.pot.set_last_bet_raise(bb, self.big_blind)

        self.pot.add(sb, self.small_blind)
        self.pot.add(bb, self.big_blind)

        self.add_action(sb, Action(Action.SMALL_BLIND, self.small_blind))
        self.add_action(bb, Action(Action.BIG_BLIND, self.big_blind))

        self.player_index = 2 if len(self.players) > 2 else 0
    
    def get_current_player(self):
        return self.players[self.player_index]
    
    def get_current_player_and_actions(self):
        player = self.get_current_player()
        actions = []
        amount_to_call = player.amount_to_call(self.pot.call_amount())

        if self.betting_round_over():
            return player, []

        if not self.pot.betting_started:
            actions = [Action(Action.CHECK), Action(Action.BET, self.pot.minimum_bet)]
        else:
            if (amount_to_call == 0 
                and player == self.big_blind_player 
                and self.stage == GameStage.PREFLOP
                and player.last_action_was(Action.BIG_BLIND)):
                actions = [Action(Action.CHECK), Action.raise_bet(self.pot.get_minimum_raise())]
            elif amount_to_call > 0:
                actions = [Action.fold(), Action.call(amount_to_call), Action.raise_bet(self.pot.get_minimum_raise())]
            else:
                actions = [Action.check(), Action.bet(self.pot.minimum_bet)]
        
        return player, actions

    def player_action(self, action: Action):
        player, actions = self.get_current_player_and_actions()

        if not any([action.action_type == a.action_type for a in actions]):
            raise ValueError(f"Invalid action {action} for player {player.name}")
        
        if action.action_type == Action.FOLD:
            self._fold(player)
            # remove player from list
            self.players = [player for player in self.players if not player.folded()]
            self.player_index -= 1
        elif action.action_type == Action.CALL:
            self._call(player)
        elif action.action_type == Action.RAISE:
            self._raise(player, action.amount)
        elif action.action_type == Action.CHECK:
            self._check(player)
        elif action.action_type == Action.BET:
            self._bet(player, action.amount)
        else:
            raise ValueError("Invalid action")
    
        self.add_action(player, player.last_action())

        # determine if move to next stage
        if len(self.players) == 1:
            self.stage = GameStage.ROUND_OVER
            return

        if len(self.action_complete_players) == len(self.players):
            self._next_stage()
        self._next_player()


    def _raise(self, player: Player, amount):
        if amount < self.pot.get_minimum_raise():
            print("Automatically put in min raise if value not met")
            amount = self.pot.get_minimum_raise() 
        
        amount_raised, all_in = player.raise_bet(amount)
        self.pot.set_last_bet_raise(player, amount)
        self.pot.add(player, amount_raised)

        if all_in:
            self.pot.split_pot()
    
    def _call(self, player: Player):
        call_amount = self.pot.call_amount()
        amount_to_call, all_in = player.call(call_amount)            

        self.pot.add(player, amount_to_call)

        if all_in:
            self.pot.split_pot()
    
    def _fold(self, player: Player):
        player.fold()
    
    def _check(self, player: Player):
        player.check()

    def deal(self):
        for player in self.players:
            player.set_cards(self.deck.draw(2))

    def _next_player(self):
        self.player_index += 1
        if self.player_index == len(self.players):
            self.player_index = 0
        
        return self.players[self.player_index]

    def _next_stage(self):
        self.player_index = 0

        for player in self.players:
            player.next_stage()
        
        self.action_complete_players = set()
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
    
    def handle_all_in(self, player: Player):
        all_in_amount = player.current_round_bet()

        for p in self.players:
            pass
        
        
            
    
    def _player_last_action_index(self, player: Player):
        index = -1
        round_actions = self.round_actions[self.stage]
        for i in range(len(round_actions)-1, -1, -1):
            
            if round_actions[i].player == player:
                index = i
                break
        
        return index
    
    def set_stage(self, stage: GameStage):
        if stage == GameStage.FLOP:
            self._next_stage()
        elif stage == GameStage.TURN:
            self._next_stage()
            self._next_stage()
        elif stage == GameStage.RIVER:
            self._next_stage()
            self._next_stage()
            self._next_stage()


    def add_action(self, player: Player, action: Action):
        if action.action_type == Action.BET or action.action_type == Action.RAISE:
            self.action_complete_players = {player}
        elif action.action_type == Action.CALL or action.action_type == Action.CHECK:
            self.action_complete_players.add(player)

        self.round_actions[self.stage].append(RoundAction(player, action))

    def current_stage_actions(self):
        return self.round_actions[self.stage]
    
    def reveal(self):
        if not self.betting_round_over():
            raise ValueError("Cannot reveal cards before the river")
    
        if len(self.board) < 5:
            print(f"Winner\n{self.players[0]}")
            return [self.players[0]], None, None
        
        winners = []
        winning_hand = None
        winning_rank = None
        best_ev = 10_000

        for player in self.players:
            hand, rank, ev = self.evaluator.best_hand_rank_eval(player.hand(), self.board)
            print(f"{player.name:<15} {rank:<15} {Card.ints_to_pretty_str(hand)}")

            if ev < best_ev:
                best_ev = ev
                winners= [player]
                winning_hand = hand
                winning_rank = rank
            elif ev == best_ev:
                winners.append(player)
        
        print(f"Winner: {', '.join([player.name for player in winners])}")

        return winners, winning_hand, winning_rank
    
    def distribute_winnings(self, players: list[Player]):
        n = len(players) 
        split = self.pot.amount // n

        for player in players:
            player.win(split)

    def board_str(self):
        return list(map(Card.int_to_str, self.board))

    def str_actions(self):
        res = ""
        for stage, actions in self.round_actions.items():
            if not actions:
                continue

            res += f"{stage.name}\n"
            for action in actions:
                res += f"{action}\n"

            res += "\n"
        
        return res
    
    def __repr__(self):
        res = f"Stage: {self.stage.name.capitalize()}\n"
        res += f"Board: {Card.ints_to_pretty_str(self.board)}\n\n"
        for player in self.players:
            res += f'{str(player)}\n'
        
        return res
    

class Poker:
    players: list[Player]
    small_blind: int
    big_blind: int
    round: Round
    small_blind_index: int

    def __init__(self, players: list[Player]=[], small_blind=10):
        self.players = players
        self.small_blind = small_blind
        self.big_blind = 2*small_blind
        self.round = None
        self.small_blind_index = 0

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
        
        for player in self.players:
            player.reset()

        round_players = self.players[self.small_blind_index:] + self.players[:self.small_blind_index]
        new_round =  Round(round_players, self.small_blind)
        self.round = new_round

        self._next_small_blind()

        return new_round
    
    def _next_small_blind(self):
        self.small_blind_index += 1
        if self.small_blind_index == len(self.players):
            self.small_blind_index = 0
