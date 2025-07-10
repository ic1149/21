import random
from os import system
from colorama import Fore as colours
import argparse


numbers = ["Ace", "2", "3", "4", "5", "6", "7",
           "8", "9", "10", "Jack", "Queen", "King"]
flowers = ["diamonds", "clubs", "hearts", "spades"]


class newDeck:
    def __init__(self):
        self.cards = [[flower] for flower in flowers]
        for flower in self.cards:
            flower += [card(number, flower[0]) for number in numbers]

        self.cardCount = 52

    def listCards(self):
        listOfCards = []
        for i in range(0, 4):
            try:
                for card in self.cards[i][1:]:

                    listOfCards += [card]
            except IndexError:
                continue  # no flower of that card

        # print(listOfCards)
        return listOfCards

    def pick(self):
        flowerEmpty = True
        while flowerEmpty:
            pickFlower = random.choice(self.cards)  # pick random flower
            if len(pickFlower) > 1:
                break
            else:
                # if the flower has no cards left, remove it
                self.cards.remove(pickFlower)

        # pick random number and remove the card
        pickNum = pickFlower.pop(random.randint(1, len(pickFlower)-1))
        self.cardCount -= 1  # one less card

        return pickNum


class card:
    def __init__(self, num, flower):
        self.num = num
        self.flower = flower
        if flower == "diamonds" or flower == "hearts":
            self.formatted = colours.RED + \
                "[" + f"{self.num} of {self.flower}" + "]" + \
                colours.RESET  # format pretty print (red)
        else:
            self.formatted = colours.RESET + \
                "[" + f"{self.num} of {self.flower}" + \
                "]"  # format pretty print


class hand:
    def __init__(self):
        self.total = 0
        self.cards = []

    def addCard(self, card, isFirst=False):
        self.cards += [card]  # add card to list
        self.total += getValue(card)  # increase card count total
        if isFirst and self.total == 1:  # base card ace is 11 instead of 1
            self.total += 10

    def clear(self):  # reset after each round
        self.cards = []
        self.total = 0


def getValue(card):
    value = numbers.index(card.num) + 1
    value = 10 if value > 10 else value
    return value


def NPC_decision(current, minChance=0.5, smart=True, omniscient=True):
    # if npc is omniscient, it knows what cards are left in the deck
    # if npc is smart, it knows what cards have not been shown (either in player hand or deck)
    if smart or omniscient:
        remainingCards = mainDeck.listCards() # only available cards
        # if omniscient they know all
        if not omniscient:
            for p in players:
                remainingCards += p.cards  # take account unknown player hands

        cardValues = []
        # print("rem cards")
        # print(remainingCards)

        for i in range(len(remainingCards)):
            # get value of each cards
            cardValues += [getValue(remainingCards[i])]

        cardValues.sort()  # put card values in order
        # print("cardvalues")
        # print(cardValues)
        valueToOvershoot = 22-current
        okCards = 0
        for v in cardValues:
            if v < valueToOvershoot:
                okCards += 1
            else:
                break  # the rest will >= current one which always overshoots if this one does

        chanceNotOvershoot = okCards/len(remainingCards)

        # see if the chance is over threshold
        return True if chanceNotOvershoot >= minChance else False

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--smart", help="smart mode", action="store_true")
parser.add_argument("-o", "--omni", help="omniscient", action="store_true")
args = parser.parse_args()

smart_mode = args.smart or args.omni
omni_mode = args.omni

# player list, True is human, False is npc
isPlayer = [True, False, False, False]
players = []  # list containing hand class items
for _ in range(0, len(isPlayer)):
    players += [hand()]

stop = "idk"

while stop != "":
    mainDeck = newDeck()  # refill deck

    # print(mainDeck.cards)
    # for i in range(0,52):
    #   pickCard = mainDeck.pick() # pick card test
    #   print(f"{pickCard.num} of {pickCard.flower}")

    for i in range(0, len(isPlayer)):
        # base card not revealed for npcs
        players[i].clear()
        baseCard = mainDeck.pick()
        players[i].addCard(baseCard, isFirst=True)
        if isPlayer[i]:
            input(f"Player {i+1}, your base card is {baseCard.formatted}")
        # input(f"Player {i+1}, your base card is {baseCard.formatted}")

        continueDraw = True
        while continueDraw:
            drawnCard = mainDeck.pick()
            players[i].addCard(drawnCard)
            # if isPlayer[i]: input(f"Player {i+1}, you have drawn {drawnCard.formatted}")
            input(
                colours.BLUE + f"Player {i+1}, you have drawn {drawnCard.formatted}" + colours.RESET)

            if players[i].total > 21:
                print(colours.RED +
                      f"Player {i+1} has overshot!" + colours.RESET)
                for c in players[i].cards:
                    print(c.formatted, end=" ")

                input("")
                break

            if isPlayer[i]:
                continueDraw = False if input(
                    "press enter to stop, type sth to draw card: ") == "" else True
            else:
                continueDraw = NPC_decision(
                    players[i].total, minChance=random.uniform(0.5, 0.7), smart=smart_mode, omniscient=omni_mode)

        print(colours.GREEN +
              f"Player {i+1} has finished the round" + colours.RESET)

    winners = []
    max = 0
    for i in range(0, len(isPlayer)):
        pTotal = players[i].total
        if 1 in [v.num for v in players[i].cards] and pTotal <= 11:
            pTotal += 10
            # if there is an Ace, and it being value 11 doesn't overshoot

        print(f"Player {i+1}, total {colours.CYAN}{pTotal}{colours.RESET}")
        if pTotal > max and pTotal <= 21:
            winners = [i+1]
            max = pTotal
        elif pTotal == max:
            winners += [i+1]

        for c in players[i].cards:
            print(c.formatted, end=" ")

        print("")

    print(colours.YELLOW + f"winners: {winners}" + colours.RESET)

    stop = input("type sth to continue, enter to stop: ")
