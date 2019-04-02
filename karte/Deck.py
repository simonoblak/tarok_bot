from karte import Card
import random


def cut_shuffle(deck, min_limit, max_limit):
    spot = random.randint(min_limit, max_limit)
    return deck[spot:] + deck[:spot]


def riffle_shuffle(deck):
    deck_half = int(len(deck) / 2)
    first_half = deck[:deck_half]
    second_half = deck[deck_half:]
    result = []
    for i in range(deck_half):
        result.append(first_half[i])
        result.append(second_half[i])
    return result


class Deck:
    def __init__(self):
        self.deck = self.create_deck()

    @staticmethod
    def create_deck():
        lines = [line.rstrip('\n') for line in open("resources/tarot_cards.txt")]
        deck = []
        for line in lines:
            name, points, rank, suit = line.split(";")
            card = Card.Card(name, points, rank, suit)
            deck.append(card)
        return deck

    def shuffle_deck(self, min_limit, max_limit, min_number_of_shuffles, max_number_of_shuffles):
        number_of_shuffles = random.randint(min_number_of_shuffles, max_number_of_shuffles)
        for i in range(number_of_shuffles):
            self.deck = cut_shuffle(self.deck, min_limit, max_limit)
            self.deck = riffle_shuffle(self.deck)
            i += 1

