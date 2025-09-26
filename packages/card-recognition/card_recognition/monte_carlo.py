import random
from collections import Counter

# Simple representation: cards 0–51
def deck():
    return list(range(52))

def hand_strength(hand, community):
    """Very naive evaluator: pair > high card"""
    cards = hand + community
    ranks = [c % 13 for c in cards]
    counts = Counter(ranks)
    if max(counts.values()) >= 2:
        return 2  # pair
    return 1  # high card

def monte_carlo_simulation(hand, community, trials=1000):
    wins, ties = 0, 0
    d = deck()
    for c in hand + community:
        d.remove(c)
    for _ in range(trials):
        random.shuffle(d)
        opp_hand = d[:2]
        remaining = d[2:2+(5-len(community))]
        final_community = community + remaining

        my_score = hand_strength(hand, final_community)
        opp_score = hand_strength(opp_hand, final_community)

        if my_score > opp_score:
            wins += 1
        elif my_score == opp_score:
            ties += 1

    win_rate = wins / trials
    tie_rate = ties / trials
    return win_rate, tie_rate

if __name__ == "__main__":
    # Example: Ace of spades (0), King of hearts (12)
    my_hand = [0, 12]
    community = []
    win_rate, tie_rate = monte_carlo_simulation(my_hand, community, trials=2000)
    print(f"Win rate: {win_rate:.2%}, Tie rate: {tie_rate:.2%}")
