from karte import Card
import random


class Deck:
    deck = []

    @staticmethod
    def create_deck(path):
        lines = [line.rstrip('\n') for line in open(path)]
        for line in lines:
            name, points, rank, suit, deck_order = line.split(";")
            card = Card.Card(name, int(points), int(rank), suit, deck_order)
            Deck.deck.append(card)

    def shuffle_deck(self, min_limit, max_limit, min_number_of_shuffles, max_number_of_shuffles):
        number_of_shuffles = random.randint(min_number_of_shuffles, max_number_of_shuffles)
        for i in range(number_of_shuffles):
            Deck.deck = self.cut_shuffle(Deck.deck, min_limit, max_limit)
            Deck.deck = self.riffle_shuffle(Deck.deck)

    def cut_shuffle(self, deck, min_limit, max_limit):
        spot = random.randint(min_limit, max_limit)
        return deck[spot:] + deck[:spot]

    def riffle_shuffle(self, deck):
        deck_half = int(len(deck) / 2)
        first_half = deck[:deck_half]
        second_half = deck[deck_half:]
        result = []
        for i in range(deck_half):
            result.append(first_half[i])
            result.append(second_half[i])
        return result

    def get_deck(self):
        return self.deck
