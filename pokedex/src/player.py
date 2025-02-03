from treys import Card
from enum import Enum
from src.hand import Hand

class ActionType(Enum):
    FOLD = 0
    CALL = 1
    RAISE = 2
    CHECK = 3
    BET = 4
    SMALL_BLIND = 5
    BIG_BLIND = 6

class Action:
    # type declarations
    FOLD = ActionType.FOLD
    CALL = ActionType.CALL
    RAISE = ActionType.RAISE
    CHECK = ActionType.CHECK
    BET = ActionType.BET
    SMALL_BLIND = ActionType.SMALL_BLIND
    BIG_BLIND = ActionType.BIG_BLIND

    def __init__(self, action_type, amount=None, amount_to_call=None, all_in=False):
        self.action_type = action_type
        self.amount = amount
        self.amount_to_call = amount_to_call
        self.all_in = all_in

    @classmethod
    def fold(cls):
        return cls(Action.FOLD)

    @classmethod
    def check(cls):
        return cls(Action.CHECK)
    
    @classmethod
    def call(cls, amount_to_call=None):
        return cls(Action.CALL, amount_to_call=amount_to_call)
    
    @classmethod
    def bet(cls, amount=None):
        return cls(Action.BET, amount)
    
    @classmethod
    def raise_bet(cls, amount):
        return cls(Action.RAISE, amount)
    
    @classmethod
    def dict_to_action(cls, action_dict):
        type_string = action_dict["type"].upper()
        action_type = ActionType[type_string]
        amount = action_dict["amount"]
        amount_to_call = action_dict["amountToCall"]

        return cls(action_type, amount, amount_to_call)
    
    def to_dict(self):
        return {
            "type": self.action_type.name,
            "amount": self.amount,
            "amountToCall": self.amount_to_call
        }

    def __repr__(self):
        if self.all_in:
            return f"ALL-IN {self.amount}"
        elif self.action_type == Action.FOLD:
            return "FOLD"
        elif self.action_type == Action.CHECK:
            return "CHECK"
        elif self.action_type == Action.CALL:
            return f"CALL {self.amount_to_call} ({self.amount})"
        elif self.action_type == Action.BET:
            return f"BET {self.amount}"
        elif self.action_type == Action.RAISE:
            return f"RAISE {self.amount}"
        elif self.action_type == Action.SMALL_BLIND:
            return f"SMALL BLIND {self.amount}"
        elif self.action_type == Action.BIG_BLIND:
            return f"BIG BLIND {self.amount}"
        
        return "UNKNOWN Action"

class RoundProfile:
    def __init__(self):
        self.bet = 0
        self.hand = None
        self.best_hand = None
        self.folded = False
        self.last_action = None
        self.all_in = False

    def next_stage(self):
        self.bet = 0
        self.last_action = None

    def reset(self):
        self.bet = 0
        self.hand = None
        self.best_hand = None
        self.folded = False
        self.last_action = None

class Player:
    def __init__(self, name, stack=100):
        self.name = name
        self.stack = stack
        self.rp = RoundProfile()

    def current_round_bet(self):
        return self.rp.bet

    def make_bet(self, amount):
        if amount < 0:
            raise ValueError("Amount must be greater than or equal to 0")
        elif amount > self.stack:
            raise ValueError("Amount must be less than or equal to stack")
        
        self.stack -= amount
        self.rp.bet += amount

    def post_small_blind(self, amount):
        self.make_bet(amount)
        self.rp.last_action = Action(Action.SMALL_BLIND, amount)
    
    def post_big_blind(self, amount):
        self.make_bet(amount)
        self.rp.last_action = Action(Action.BIG_BLIND, amount)
    
    def bet(self, amount):
        all_in = False

        if amount <= 0 or amount > self.stack:
            raise ValueError("Amount must be greater than or equal to 0 and less than or equal to stack")
        elif amount == self.stack:
            self.rp.all_in = True
            all_in = True

        self.make_bet(amount)
        self.rp.last_action = Action(Action.BET, amount, all_in=all_in)
    
    def fold(self):
        self.rp.folded = True
        self.rp.last_action = Action(Action.FOLD)
    
    def check(self):
        self.rp.last_action = Action(Action.CHECK)
    
    def call(self, amount):
        current_bet = self.current_round_bet()
        if amount < current_bet:
            raise ValueError(f"Amount must be greater than or equal to {current_bet}")
        
        all_in = False
        amount_to_call = self.amount_to_call(amount)

        if amount_to_call > self.stack:
            amount = self.stack
            amount_to_call = self.stack
            self.rp.all_in = True
            all_in = True

        self.make_bet(amount_to_call)
        self.rp.last_action = Action(Action.CALL, amount, amount_to_call, all_in=all_in)

        return amount_to_call, all_in
    
    def amount_to_call(self, amount):
        return amount - self.current_round_bet()
    
    def raise_bet(self, amount):
        if amount < 0:
            raise ValueError("Raise amount must be greater than or equal to 0")
        
        all_in = False
        amount_raised = amount - self.current_round_bet()
        if amount > self.stack or amount_raised < 0:
            raise ValueError("Raise amount must be positive and less than or equal to stack")
        elif amount == self.stack:
            self.rp.all_in = True
            

        self.make_bet(amount_raised)
        self.rp.last_action = Action(Action.RAISE, amount, all_in=all_in)

        return amount_raised, all_in
    
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

    def str_hand(self):
        return list(map(Card.int_to_str, self.rp.hand))

    def best_hand(self):
        return self.rp.best_hand
    
    def folded(self):
        return self.rp.folded
    
    def last_action(self) -> Action:
        return self.rp.last_action
    
    def last_action_was(self, action_type):
        return self.rp.last_action.action_type == action_type
 
    def next_stage(self):
        self.rp.next_stage()
        
    def reset(self):
        self.rp.reset()
    
    def to_dict(self):
        return {
            "name": self.name,
            "stack": self.stack,
            "hand": Hand.ints_to_str(self.rp.hand) if self.rp.hand else None,
            "action": self.rp.last_action.to_dict() if self.rp.last_action else None
        }
    
    def __repr__(self):
        res = f"{self.name:<15} {self.stack:<5}"
        if self.rp.hand:
            res += f'{Card.ints_to_pretty_str(self.rp.hand):<15}'

        return res