from src.poker import Poker

def main():
    game = Poker()
    game.add_player_by_name("Harry Potter")
    game.add_player_by_name("Cho Chang")
    game.add_player_by_name("Luna Lovegood")

    game.set_stacks(1000)
    round = game.new_round()

    # Start round 1
    round.deal()
    print(round)
    round.start_betting_round()
    
    print()
    print(round)
    round.start_betting_round()
    round.start_betting_round()
    round.start_betting_round()
    
    print(round)

    round.reveal()


if __name__ == "__main__":
    main()