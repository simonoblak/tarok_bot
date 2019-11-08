import Configuration
import random

config = Configuration.Configuration().get_config()


class RandomBot:
    def __init__(self, cards):
        # self.deck = Deck.Deck().get_deck()
        self.cards = cards
        self.king_indexes = []
        self.playing_suite = ""

    def set_cards(self, cards):
        self.cards = cards

    def choose_king(self):
        suits = config["suit_signs"].split(",")
        for card in self.cards:
            if card.name.lower() == "king":
                suits.remove(card.alt[0])
        self.king_indexes = self.get_king_indexes()
        self.playing_suite = random.choice(suits)
        return self.playing_suite

    def choose_talon_step_1(self, n, talon):
        for index, card in enumerate(talon):
            if card.alt == self.playing_suite + "8":
                return index

        return talon.index(random.choice(talon))

    def choose_talon_step_2(self, n, non_disabled_card_indexes):
        return random.sample(set(non_disabled_card_indexes), n)

    def get_king_indexes(self):
        indexes = []
        for index, card in enumerate(self.cards):  # range(0, len(self.cards)):
            if card.name.lower() == "king":
                indexes.append(index)
        return indexes

    def play_card(self, non_disabled_card_indexes, table, suite):
        return random.sample(set(non_disabled_card_indexes), 1)[0]
