from treys import Evaluator
from itertools import combinations
from treys import Card

class Hand:
    cards: list[int]
    rank: str
    eval: int

    def __init__(self, cards, rank, eval):
        if len(cards) != 5:
            raise ValueError("Hand must have 5 cards")
        
        self.cards = cards
        self.rank = rank
        self.eval = eval

    def ints_to_str(hand: list[int]):
        if not hand:
            return []
        
        return [Card.int_to_str(i) for i in hand]
    
    def __repr__(self):
        return f"{self.cards} ({self.rank})"  

class HandEvaluator:
    def __init__(self):
        self.evaluator = Evaluator()
    

    def best_hand_rank_eval(self, hand, board):
        cards = sorted(hand + board)
        minimum = 10_000
        best_hand = None

        for combo in combinations(cards, 5):
            cb_list = list(combo)
            score = self.evaluator.evaluate(cb_list, [])
            if score < minimum:
                minimum = score
                best_hand = cb_list
        
        rank = self.evaluator.get_rank_class(minimum)
        rank_str = self.evaluator.class_to_string(rank)
        return best_hand, rank_str, minimum