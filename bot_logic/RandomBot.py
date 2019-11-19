import Configuration
import random

config = Configuration.Configuration().get_config()


class RandomBot:
    def __init__(self, cards):
        self.cards = cards
        self.king_indexes = []
        self.playing_suite = ""
        self.game = -1

    def set_cards(self, cards):
        self.cards = cards

    def choose_king(self):
        suits = config["suit_signs"].split(",")
        for card in self.cards:
            if card.rank == "8":
                suits.remove(card.suit)
        self.playing_suite = random.choice(suits)
        return self.playing_suite

    def choose_talon_step_1(self, n, talon):
        for index, card in enumerate(talon):
            if card.alt == self.playing_suite + "8":
                return index

        return talon.index(random.choice(talon))

    def choose_talon_step_2(self, n, non_disabled_card_indexes):
        return random.sample(set(non_disabled_card_indexes), n)

    def play_card(self, non_disabled_card_indexes, table, suite):
        return random.sample(set(non_disabled_card_indexes), 1)[0]
