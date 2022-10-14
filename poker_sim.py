"""First working version of code."""

from random import choice, randint, shuffle
from collections import namedtuple
from itertools import cycle, combinations

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
        

class Chips:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "$%.2f" % self.value

    def __lt__(self, other):
        if isinstance(other, Chips):
            return self.value < other.value
        return self.value < other

    def __le__(self, other):
        if isinstance(other, Chips):
            return self.value <= other.value
        return self.value <= other

    def __gt__(self, other):
        if isinstance(other, Chips):
            return self.value > other.value
        return self.value > other

    def __ge__(self, other):
        if isinstance(other, Chips):
            return self.value >= other.value
        return self.value >= other

    def __add__(self, other):
        if isinstance(other, Chips):
            return Chips(self.value + other.value)
        return Chips(self.value + other)

    def __radd__(self, other):
        if isinstance(other, Chips):
            return Chips(other.value + self.value)
        return Chips(other + self.value)

    def __sub__(self, other):
        if isinstance(other, Chips):
            return Chips(self.value - other.value)
        return Chips(self.value - other)

    def __rsub__(self, other):
        if isinstance(other, Chips):
            return Chips(other.value - self.value)
        return Chips(other - self.value)

    def __mul__(self, other):
        if isinstance(other, Chips):
            return Chips(self.value * other.value)
        return Chips(self.value * other)

    def __rmul__(self, other):
        if isinstance(other, Chips):
            return Chips(other.value * self.value)
        return Chips(other * self.value)

    def __ne__(self, other):
        if isinstance(other, Chips):
            return self.value != other.value
        return self.value != other

    def __eq__(self, other):
        if isinstance(other, Chips):
            return self.value == other.value
        return self.value == other


class Table:
    def __init__(self, players):
        self.players = players
        self.playerCycle = cycle(players)
        self.livePlayers = len(players)
        self.lastLivePlayer = False
        self.foldsAndAllIns = 0
        self.remainingActions = len(players)
        self.lastAction = False
        self.deck = Deck()
        self.commCards = []
        self.sb = Chips(0.01)
        self.bb = Chips(0.02)
        self.currBet = self.bb
        self.minRaise = self.bb
        self.notionalPot = Chips(0.00)
        self.pots = []
        self.rounds = ["preflop", "flop", "turn", "river"]
        self.currRound = self.rounds[0]

    def showdown(self):
        from showdown import rankHand
        while self.pots:
            pot = self.pots.pop()
            for player in pot.contestants:
                if not player.hand:
                    hands = combinations((player.hole + self.commCards), 5)
                    best = 0
                    for hand in hands:
                        score = rankHand(hand)
                        if score > best:
                            best = score
                    player.hand = best

            pot.contestants.sort(key=lambda x: x.hand)
            winner = pot.contestants.pop() # Sort out chopped pots later
            winner.stack += pot.value
            print("{} wins {}".format(winner.name, pot.value))
        
        
    def advanceRound(self):
        index = self.rounds.index(self.currRound)
        self.currRound = self.rounds[index+1]
        print("---{}---".format(self.currRound))
        if self.currRound == "flop":
            self.drawCards(3, self.commCards)
        elif self.currRound == "turn" or self.currRound == "river":
            self.drawCards(1, self.commCards)
        board = [str(card) for card in self.commCards]
        print(board)

        for player in self.players:
            if not player.hasFolded and not player.allIn:
                player.fullRaiseThreshold = Chips(0.00)

        self.playerCycle = cycle(players)
        self.currBet = Chips(0.00)
        self.minRaise = self.bb
        
    def winByFolds(self):
        while self.pots:
            pot = self.pots.pop()
            self.lastLivePlayer.stack += pot.value
            print("{} wins {}".format(self.lastLivePlayer.name,
                                      pot.value))

    def handleBet(self, player, amount):
        diff = player.bet(amount)
        table.notionalPot += diff

    def drawCards(self, number, target):
        cards = [self.deck.pop() for _ in range(number)]
        target += cards

    def deal(self):
        self.deck.shuffle()
        for player in self.players:
            self.drawCards(2, player.hole)

    def printPlayer(self, player):
        name = player.name.ljust(8)
        hole = "[{} {}]".format(player.hole[0], player.hole[1])
        stack = player.stack
        wager = player.wager

        text = "{} {} Stack {} Wager {}".format(name, hole, stack, wager)
        print(text)

    def implement(self, player, decision):
        player.hasAction = False
        self.remainingActions -= 1
        
        if decision == "fold":
            player.hasFolded = True
            self.livePlayers -= 1
            self.foldsAndAllIns += 1
            print("{} folds".format(player.name))
            
        elif decision == "call":
            if player.maxBet <= self.currBet:
                self.handleBet(player, player.maxBet)
                player.allIn = True
                self.foldsAndAllIns += 1
                print("{} calls {} and is all in".format(player.name,
                                                         player.maxBet))
            else:
                self.handleBet(player, self.currBet)
                player.fullRaiseThreshold = self.currBet + self.minRaise
                if self.currBet == 0:
                    print("{} checks".format(player.name))
                else:
                    print("{} calls {}".format(player.name,
                                               self.currBet))
                
        else:   # Raise (decision is a quantity of chips)
            self.reopenAction(player)
            self.handleBet(player, decision)
            if decision < self.currBet + self.minRaise:
                self.currBet = decision
                player.allIn = True
                self.foldsAndAllIns += 1
                print("{} bets {} and is all in".format(player.name,
                                                        self.currBet))
            else:
                self.minRaise = decision - self.currBet
                self.currBet = decision
                player.fullRaiseThreshold = self.minRaise + self.currBet
                print("{} bets {}".format(player.name, self.currBet))

    def commitToPot(self, winByFolds=False):
        byWager = sorted(self.players, key=lambda x: x.wager)
        first = byWager[-1]
        second = byWager[-2]
        if not winByFolds:
            if first.wager > second.wager:
                diff = first.wager - second.wager
                first.wager -= diff
        else:
            print("Returning uncalled bet {} to {}".format(first.wager,
                                                           first.name))

        carry = Chips(0.00)
        firstPass = True
        n = len(byWager)
        for player in byWager:
            amount = player.wager
            if amount == 0:
                pass
            elif player.hasFolded:
                carry += amount
                player.wager -= amount
            else:
                index = byWager.index(player)
                contestants = byWager[index:]
                for contestant in contestants:
                    contestant.wager -= amount
                if winByFolds:
                    value = carry
                else:
                    value = n * amount + carry

                if self.pots and firstPass:
                    self.pots[-1].value += value
                    firstPass = False
                else:
                    self.pots.append(Pot(value, contestants))
            n -= 1

    def reopenAction(self, case):
        if case == "nextRound":
            for player in self.players:
                if not player.hasFolded and not player.allIn:
                    player.hasAction = True
                    self.remainingActions += 1
        else:
            player = case
            index = self.players.index(player)
            otherPlayers = self.players[:index] + self.players[index+1:]
            for otherPlayer in otherPlayers:
                if not otherPlayer.hasFolded and not otherPlayer.allIn:
                    if not otherPlayer.hasAction:
                        otherPlayer.hasAction = True
                        self.remainingActions += 1

    def updateLastAction(self):
        """
        Determines if 1 action left (all others have folded or all-in).
        Removes option to raise (only call/fold), as nobody left to raise.
        """
        if self.foldsAndAllIns == len(self.players) - 1:
            self.lastAction = True

    def updateLastLivePlayer(self):
        if self.livePlayers == 1:
            for player in self.players:
                if not player.hasFolded:
                    self.lastLivePlayer = player
                    break
        
class Pot:
    def __init__(self, value=Chips(0.00), contestants=[]):
        self.value = value
        self.contestants = contestants
    def update(self, amount):
        self.value += amount


class Player:   
    def __init__(self, name):       
        self.name = name
        self.hole = []
        self.stack = Chips(2.00)
        self.startingStack = self.stack
        self.wager = Chips(0.00)
        self.maxBet = self.stack + self.wager
        self.fullRaiseThreshold = Chips(0.00)
        self.hand = None
        self.hasFolded = False
        self.hasAction = True
        self.allIn = False

    def bet(self, amount):
        diff = amount - self.wager
        self.stack -= diff
        self.wager += diff
        return diff

    def decide(self, currBet, minRaise, lastAction):
        """lastAction comes from Table - restricts actions if nobody left to raise"""
        self.maxBet = self.stack + self.wager
        if currBet == 0 or self.wager == currBet:    # No fold; unopened
            choices = ["raise", "call"]
        elif currBet >= self.fullRaiseThreshold and currBet < self.maxBet and not lastAction:
            choices = ["raise", "call", "fold"]
        else:   # Player is last in hand, or action didn't fully reopen
            choices = ["call", "fold"]

        decision = choice(choices)

        if decision == "raise":
            size = randint(1,5)
            amount = minRaise * size + currBet
            if amount > self.maxBet:
                amount = self.maxBet
            return amount

        return decision
            

def main():
    sbPosted = False
    bbPosted = False
    
    while True:
        player = next(table.playerCycle)

        if bbPosted:
            if not player.hasFolded and player.hasAction:
                table.printPlayer(player)
                decision = player.decide(table.currBet, table.minRaise, table.lastAction)
                table.implement(player, decision)
                
        else:
            if sbPosted:
                table.handleBet(player, table.bb)
                print("{} posts big blind".format(player.name))
                bbPosted = True
                table.deal()
            else:
                table.handleBet(player, table.sb)
                print("{} posts small blind".format(player.name))
                sbPosted = True
                
        table.updateLastAction()
        table.updateLastLivePlayer()
        if table.lastLivePlayer:
            table.commitToPot(winByFolds=True)
            table.winByFolds()
            break
        if not table.remainingActions:
            table.commitToPot()
            if table.currRound != "river":
                table.advanceRound()
                table.reopenAction("nextRound")
            else:
                table.showdown()
                break
    print("End of game")
        
                
if __name__ == "__main__":
    names = "Alan Bob Charlie Daniel Eddie Frank".split()
    players = [Player(name) for name in names]
    table = Table(players)
    main()
