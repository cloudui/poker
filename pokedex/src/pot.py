from .player import Player

class Pot:
    amount: int
    side_pots: list
    last_bet_raise: tuple
    min_raise_amount: int
    betting_started: bool
    current_round_bet: int
    minimum_bet: int
    contributions: dict[Player, int]

    def __init__(self, minimum_bet=0):
        self.amount = 0
        self.side_pots = []
        self.last_bet_raise = (None, 0)
        self.min_raise_amount = minimum_bet
        self.betting_started = False
        self.current_round_bet = 0
        self.minimum_bet = minimum_bet

        self.contributions = {}


    def add(self, player: Player, amount):
        if player not in self.contributions:
            self.contributions[player] = 0
        self.contributions[player] += amount

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
    
    def split_pot(self):
        players = self.contributions.keys()

        all_in_amts = sorted([self.contributions[player] for player in players if player.all_in()])
        contributions = {p: amount for p, amount in self.contributions.items()}

        pots = []
        last_amount = 0
        for amount in all_in_amts:
            amount_diff = amount - last_amount
            eligible_players = []
            side_pot_amount = 0
            # print('pot')
            for player in players:
                # print(player.name, contributions[player], amount_diff)
                if contributions[player] >= amount_diff:
                    
                    side_pot_amount += amount_diff
                    contributions[player] -= amount_diff
                    eligible_players.append(player)
                else:
                    side_pot_amount += contributions[player]
                    contributions[player] = 0
            
            pots.append((side_pot_amount, eligible_players))
            last_amount = amount

        self.side_pots = pots

        return pots
            

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