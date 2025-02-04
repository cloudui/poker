from .player import Player

class Pot:
    amount: int
    side_pots: list[tuple[int, set[Player]]]
    last_bet_raise: tuple
    min_raise_amount: int
    betting_started: bool
    current_round_bet: int
    minimum_bet: int
    last_full_raise: int
    contributions: dict[Player, int]

    def __init__(self, minimum_bet=0):
        self.amount = 0
        self.side_pots = []
        self.last_bet_raise = (None, 0)
        self.min_raise_amount = minimum_bet
        self.betting_started = False
        self.current_round_bet = 0
        self.minimum_bet = minimum_bet
        self.last_full_raise = 0

        self.contributions = {}


    def add(self, player: Player, amount):
        if player not in self.contributions:
            self.contributions[player] = 0
        self.contributions[player] += amount

        self.amount += amount
        self.current_round_bet += amount
        self.betting_started = True
    
    def set_last_bet_raise(self, player, amount, all_in=False):
        raise_amount = amount - self.last_bet_raise[1]
        full_raise = raise_amount >= self.min_raise_amount
    
        if not full_raise and not all_in:
            raise ValueError("Must min raise or go all in")
        
        if full_raise:
            self.min_raise_amount = amount - self.last_bet_raise[1]
            self.last_full_raise = amount

        self.last_bet_raise = (player, amount)
    
    def get_last_bet_raise(self):
        return self.last_bet_raise
    
    def get_minimum_raise(self):
        return self.min_raise_amount + self.last_bet_raise[1]

    def call_amount(self):
        return self.last_bet_raise[1]
    
    def split_pot(self, final=False):
        players = self.contributions.keys()

        all_in_amts = sorted([self.contributions[player] for player in players if player.all_in()])
        contributions = {p: amount for p, amount in self.contributions.items()}

        pots = []
        last_amount = 0
        for amount in all_in_amts:
            amount_diff = amount - last_amount
            eligible_players = set()
            side_pot_amount = 0
            # print('pot')
            for player in players:
                # print(player.name, contributions[player], amount_diff)
                if contributions[player] >= amount_diff:
                    side_pot_amount += amount_diff
                    contributions[player] -= amount_diff
                    if not player.folded():
                        eligible_players.add(player)
                else:
                    side_pot_amount += contributions[player]
                    contributions[player] = 0
            
            pots.append((side_pot_amount, eligible_players))
            last_amount = amount
        
        if final:
            remainder_pot = self.amount - sum([pot[0] for pot in pots])
            eligible_players = {player for player in self.contributions.keys()
                                if contributions[player] > 0 and not player.folded()}
            pots.append((remainder_pot, eligible_players))

        self.side_pots = pots

        return pots
    
    def final_pots(self):
        pots = self.split_pot(final=True)
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