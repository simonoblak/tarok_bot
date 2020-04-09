import Configuration
import random

config = Configuration.Configuration().get_config()


class RandomBot:
    def __init__(self, cards):
        self.cards = cards
        self.king_indexes = []
        self.playing_suite = ""
        self.game = -1
        self.ally = ""
        self.method_outcomes = {"king": -1, "talon1": -1, "talon2": -1}

    def set_cards(self, cards):
        """
        Interface method.
        :param cards:
        :return:
        """
        self.cards = cards

    def init_round(self):
        """
        Interface method.
        :return:
        """
        self.playing_suite = ""
        self.king_indexes = []

    def choose_king(self):
        """
        Interface method.
        :return:
        """
        suits = config["suit_signs"].split(",")
        for card in self.cards:
            if card.is_king:
                suits.remove(card.suit)
        self.playing_suite = random.choice(suits)
        return self.playing_suite

    def choose_talon_step_1(self, n, talon):
        """
        Interface method.
        :param n:
        :param talon:
        :return:
        """
        for index, card in enumerate(talon):
            if card.alt == self.playing_suite + "8":
                return index

        return talon.index(random.choice(talon))

    def choose_talon_step_2(self, n, non_disabled_card_indexes):
        """
        Interface method.
        :param n:
        :param non_disabled_card_indexes:
        :return:
        """
        return_cards = []
        random_card_indexes = random.sample(set(non_disabled_card_indexes), n)
        for i in random_card_indexes:
            return_cards.append(self.cards[i])
        return return_cards

    def play_card(self, non_disabled_card_indexes, table, suite, playing_status):
        """
        Interface method.
        :param non_disabled_card_indexes:
        :param table:
        :param suite:
        :return:
        """
        return self.cards[random.sample(set(non_disabled_card_indexes), 1)[0]]

    def set_suit_helper_objects_and_tarots(self, table, suit_of_table, talon_cards):
        """
        Interface method
        :param table:
        :param suit_of_table:
        :param talon_cards:
        :return:
        """
        return
