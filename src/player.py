from treys import Card

class RoundProfile:
    def __init__(self):
        self.bet = 0
        self.hand = None
        self.best_hand = None
        self.folded = False

    def reset(self):
        self.bet = 0
        self.hand = None
        self.best_hand = None
        self.folded = False

class Player:
    def __init__(self, name, stack=100):
        self.name = name
        self.stack = stack
        self.rp = RoundProfile()

    def current_round_bet(self):
        return self.rp.bet
    
    def bet(self, amount):
        self.stack -= amount
        self.rp.bet += amount
    
    def fold(self):
        self.rp.folded = True
    
    def win(self, amount):
        self.stack += amount

    def set_stack(self, amount):
        self.stack = amount

    def set_cards(self, cards: list[Card]):
        self.rp.hand = cards

    def set_best_hand(self, cards: list[Card]):
        self.rp.best_hand = cards

    def hand(self):
        return self.rp.hand

    def best_hand(self):
        return self.rp.best_hand
    
    def folded(self):
        return self.rp.folded
 
    def reset(self):
        self.rp.reset()
    
    def __repr__(self):
        res = f"{self.name:<15} {self.stack:<5}"
        if self.rp.hand:
            res += f'{Card.ints_to_pretty_str(self.rp.hand):<15}'

        return res