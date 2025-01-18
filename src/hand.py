from treys import Evaluator
from itertools import combinations

class Hand:
    def __init__(self, cards, rank):
        self.cards = cards
        self.rank = rank
    
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