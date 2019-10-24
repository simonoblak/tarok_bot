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

    def set_cards(self, cards):
        self.cards = cards

    def choose_king(self):
        suits = config["suits"].split(",")
        for card in self.cards:
            if card.name.lower() == "king":
                suits.remove(card.suit)
        self.king_indexes = self.get_king_indexes()
        random_suite = random.choice(suits)
        return random_suite

    def choose_talon_step_1(self, n, talon):
        suits = config["suits"].split(",")
        for card in self.cards:
            if card.name.lower() == "king":
                suits.remove(card.suit)

        return 0

    def choose_talon_step_2(self, n, non_disabled_card_indexes):
        return random.sample(set(non_disabled_card_indexes), n)

    def get_king_indexes(self):
        indexes = []
        for i in range(0, len(self.cards)):
            if self.cards[i].name.lower() == "king":
                indexes.append(i)
        return indexes

    def play_card(self, non_disabled_card_indexes):
        return random.sample(set(non_disabled_card_indexes), 1)[0]



