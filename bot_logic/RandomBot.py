import Configuration
import random
from ProjectConstants.CardRanks import CardRanks
from Logs import Logs

config = Configuration.Configuration().get_config()


class RandomBot:
    def __init__(self, cards):
        self.cards = cards
        self.king_indexes = []
        self.playing_suite = ""
        self.game = -1
        self.ally = ""
        self.players = {}
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
        self.game = -1
        self.ally = ""
        self.players = {}
        self.method_outcomes = {"king": -1, "talon1": -1, "talon2": -1}

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
        message = "RandomBot.choose_talon_step_1(): "
        for index, card in enumerate(talon):
            if card.alt == self.playing_suite + CardRanks.KING:
                Logs.debug_message(message + "Choosing my king.")
                return index

        return talon.index(random.choice(talon))

    def choose_talon_step_2(self, n, non_disabled_card_indexes):
        """
        Interface method.
        :param n:
        :param non_disabled_card_indexes:
        :return:
        """
        message = "RandomBot.choose_talon_step_2(): "
        return_cards = []
        color_indexes = []
        for i in non_disabled_card_indexes:
            if not self.cards[i].is_tarot and not self.cards[i].is_king:
                color_indexes.append(i)

        if len(color_indexes) < self.game:
            color_indexes = non_disabled_card_indexes
            Logs.debug_message(message + "Including tarots...")
        random_card_indexes = random.sample(set(color_indexes), n)

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
        message = "RandomBot.set_suit_helper_objects_and_tarots(): "
        for stack in table:
            if stack == "stack0":
                continue
            if table[stack] != "":
                alt = table[stack]
                self.players[stack].cards.append(alt)
                if isinstance(alt, int):
                    self.players[stack].tarot_count += 1
                    if alt == 1 or alt == 21 or alt == 22:
                        self.players[stack].trula_count += 1
                    return
                # od tu naprej so samo barve
                if alt[1] == CardRanks.KING:
                    self.players[stack].king_count += 1
            else:
                Logs.error_message(message + "table[stack] is empty?!?")
