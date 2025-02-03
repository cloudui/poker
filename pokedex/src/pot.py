from .player import Player

class SidePot:
    def __init__(self, amount, players=[]):
        self.amount = amount
        self.players = players

    def add(self, amount):
        self.amount += amount

    def __repr__(self):
        return f"SidePot: {self.amount} from {self.players}"

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
    
    def handle_all_in(self, player, actions):
        pass

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
    
    def round_stats_str(self):
        return f"Current round total: {self.current_round_bet}\nPot Total: {self.amount}"

    def __repr__(self):
        return f"Pot: {self.amount}"