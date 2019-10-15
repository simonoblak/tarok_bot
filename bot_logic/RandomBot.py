from karte import Deck
from karte import Card
import Configuration
import random

config = Configuration.Configuration().get_config()


class RandomBot:
    def __init__(self, cards):
        # self.deck = Deck.Deck().get_deck()
        self.cards = cards
        self.king_indexes = []

    def choose_king(self):
        suits = config["suits"].split(",")
        for card in self.cards:
            if card.name.lower() == "king":
                suits.remove(card.suit)
        self.king_indexes = self.get_king_indexes()
        random_suite = random.choice(suits)
        return random_suite

    def choose_talon(self, n, talon):
        suits = config["suits"].split(",")
        for card in self.cards:
            if card.name.lower() == "king":
                suits.remove(card.suit)

        return 0

    def get_king_indexes(self):
        indexes = []
        for i in range(0, len(self.cards)):
            if self.cards[i].name.lower() == "king":
                indexes.append(i)
        return indexes



