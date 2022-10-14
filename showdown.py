from collections import namedtuple, Counter
from itertools import combinations
from random import choice, shuffle

"""Testing functions"""
def randomHand(deck, n):
    return [choice(deck) for i in range(n)]

def displayHand(hand):
    res = ""
    for card in hand:
        res += str(card) + " "
    return res

def rankRandomHand(deck):
    while True:
            hand = randomHand(deck, 5)
            print(displayHand(hand))
            print(rankHand(hand))
            again = input("Again? ")
            if again not in ["y", "Y"]:
                break
"""\Testing functions"""

Rank = namedtuple("Rank", ["value", "name"])

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        return "%s%s" % (self.rank.name, self.suit)

    def __lt__(self, other):
        return self.rank.value < other

    def __gt__(self, other):
        return self.rank.value > other

    def __eq__(self, other):
        return self.rank.value == other

    def __hash__(self):
        return hash((self.rank, self.suit))

    def __sub__(self, other):
        return self.rank.value - other

    def __rsub__(self, other):
        return other - self.rank.value

class Deck:
    values = [i for i in range(2, 15)]
    names = [str(i) for i in range(2, 10)] + list("TJQKA")
    ranks = [Rank(value, name) for value, name in zip(values, names)]
    suits = "♠ ♣ ♥ ♦".split()

    def __init__(self):
        self.cards = [Card(rank, suit) for suit in self.suits
                                       for rank in self.ranks]
    def __len__(self):
        return len(self.cards)
        
    def __getitem__(self, position):
        return self.cards[position]

    def __setitem__(self, position, value):
        self.cards[position] = value

    def pop(self, index=-1):
        return self.cards.pop(index)

    def shuffle(self):
        shuffle(self.cards)

def rankHand(hand):
    sortedHand = sorted(hand)
    countedHand = counted(hand)
    
    if royalFlush(sortedHand, countedHand):
        return 9
    if straightFlush(sortedHand, countedHand):
        return 8
    if fourOfAKind(countedHand):
        return 7
    if fullHouse(countedHand):
        return 6
    if flush(hand):
        return 5
    if straight(sortedHand, countedHand):
        return 4
    if threeOfAKind(countedHand):
        return 3
    if twoPair(countedHand):
        return 2
    if onePair(countedHand):
        return 1
    return 0

def counted(hand):
    values = [card.rank.value for card in hand]
    return Counter(values)

def royalFlush(sortedHand, countedHand):
    if straightFlush(sortedHand, countedHand):
        if sortedHand[0] == 10:
            return True
    return False

def straightFlush(sortedHand, countedHand):
    if straight(sortedHand, countedHand):
        if flush(sortedHand):
            return True
    return False

def fourOfAKind(countedHand):
    for k, v in countedHand.items():
        if v == 4:
            return True
    return False

def fullHouse(countedHand):
    if threeOfAKind(countedHand):
        for k, v in countedHand.items():
            if v == 2:
                return True
    return False

def flush(hand):
    for card in hand[1:]:
        if card.suit != hand[0].suit:
            return False
    return True

def straight(sortedHand, countedHand):
    for k, v in countedHand.items():
        if v != 1:
            return False
    if sortedHand[-1] - sortedHand[0] == 4:
            return True
    elif sortedHand[-1] - sortedHand[0] == 12:
        if sortedHand[-2] - sortedHand[0] == 3:
            return True
    return False

def threeOfAKind(countedHand):
    for k, v in countedHand.items():
        if v == 3:
            return True
    return False

def twoPair(countedHand):
    second = False
    for k, v in countedHand.items():
        if v == 2:
            if second:
                return True
            second = True
    return False

def onePair(countedHand):
    for k, v in countedHand.items():
        if v == 2:
            return True
    return False

if __name__ == "__main__":
    """
    Deck ranges from 2 -> A in each suit
    0  - 12 = ♠
    13 - 25 = ♣
    26 - 38 = ♥
    39 - 52 = ♦
    """
    deck = Deck()
    
    testRoyalFlush = deck[8:13]
    testStraightFlush = deck[7:12]
    testFourOfAKind = [deck[0], deck[13], deck[26], deck[39], deck[1]]
    testFullHouse = [deck[0], deck[13], deck[26], deck[1], deck[14]]
    testFlush = [deck[0], deck[2], deck[4], deck[6], deck[8]]
    testStraight = deck[1:5] + [deck[13]]
    testThreeOfAKind = [deck[0], deck[13], deck[26]] + deck[1:3]
    testTwoPair = [deck[0], deck[13], deck[1], deck[14], deck[2]]
    testOnePair = [deck[0], deck[13], deck[2], deck[4], deck[6]]
    testHighCard = [deck[0], deck[6], deck[12], deck[18], deck[24]]

    testWheel = deck[:4] + [deck[25]]
    testWheelFlush = deck[:4] + [deck[12]]

    tests = [
        testRoyalFlush,
        testStraightFlush,
        testFourOfAKind,
        testFullHouse,
        testFlush,
        testStraight,
        testThreeOfAKind,
        testTwoPair,
        testOnePair,
        testHighCard,
        testWheel,
        testWheelFlush
        ]
    
    for test in tests:
        print(displayHand(test))
        print(rankHand(test))
