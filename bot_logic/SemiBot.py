from karte import Deck
from karte import Card
import bot_logic.Tools
import Configuration
import random

config = Configuration.Configuration().get_config()


class SemiBot:
    def __init__(self, cards):
        self.deck = Deck.Deck().get_deck()
        self.cards = cards

    def choose_king(self):
        suits = config["suits"].split(",")
        for card in self.cards:
            if card.name.lower() == "king":
                suits.remove(card.suit)

        random_suite = random.choice(suits)

