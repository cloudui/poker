
from src.poker import Poker, GameStage
from src.player import Player, Action

def test1():
    players = [
        Player("Harry Potter", 1000),
        Player("Cho Chang", 1000),
        Player("Luna Lovegood", 75),
        Player("Ron Weasley", 200)
    ]

    poker = Poker(players=players, small_blind=10)

    round = poker.new_round()
    round.deal()
    round.set_stage(GameStage.FLOP)

    round.player_action(Action.bet(100))
    round.player_action(Action.call())
    round.player_action(Action.call()) # All in for 75
    round.player_action(Action.raise_bet(200)) 

    # print(round)
    print(round.str_actions())


def test2():
    players = [
        Player("Harry Potter", 1000),
        Player("Cho Chang", 1000),
        Player("Luna Lovegood", 75),
        Player("Ron Weasley", 1000),
        Player("Hermione Granger", 150),
        Player("Ginny Weasley", 25),
        Player("Albus Dumbledore", 1000),
    ]

    poker = Poker(players=players, small_blind=10)

    round = poker.new_round()
    round.deal()
    round.set_stage(GameStage.FLOP)

    round.player_action(Action.bet(100))
    round.player_action(Action.call())
    round.player_action(Action.call()) # All in for 75
    round.player_action(Action.raise_bet(200))
    round.player_action(Action.call()) # all in for 150
    round.player_action(Action.call()) # all in for 25

    for pot, eligible_players in round.pot.side_pots:
        print(pot, len(eligible_players))
    print(round.pot.amount - sum([pot[0] for pot in round.pot.side_pots]))
    print(round.pot.amount)

    # print(round)
    print(round.str_actions())

def test3():
    players = [
        Player("Harry Potter", 50),
        Player("Cho Chang", 1000),
        Player("Luna Lovegood", 75),
        Player("Ron Weasley", 1000),
        Player("Hermione Granger", 150),
        Player("Ginny Weasley", 25),
    ]

    poker = Poker(players=players, small_blind=10)

    round = poker.new_round()
    round.deal()
    round.set_stage(GameStage.FLOP)

    round.player_action(Action.check())
    round.player_action(Action.bet(100))
    round.player_action(Action.call()) # All in for 75
    round.player_action(Action.raise_bet(200))
    round.player_action(Action.call()) # all in for 150
    round.player_action(Action.call()) # all in for 25
    round.player_action(Action.call()) # all in for 50 (harry)

    for pot, eligible_players in round.pot.side_pots:
        print(pot, len(eligible_players))
    print(round.pot.amount - sum([pot[0] for pot in round.pot.side_pots]))
    print(round.pot.amount)

    # print(round)
    print(round.str_actions())

test3()