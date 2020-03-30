import Configuration
import random
from Logs import Logs

config = Configuration.Configuration().get_config()


class SemiBot:
    def __init__(self, cards):
        self.cards = cards
        self.king_indexes = []
        self.playing_suite = ""
        self.game = -1
        self.ally = ""
        Logs.init_logs()

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
            bad_suit = ""
            if card.is_king:
                suits.remove(card.suit)
            elif not card.is_tarot:
                for suit in suits:
                    if suit == card.suit:
                        bad_suit = card.suit
                        break

            if bad_suit != "":
                suits.remove(bad_suit)

        self.playing_suite = random.choice(suits) if len(suits) > 0 else random.choice(config["suit_signs"].split(","))
        return self.playing_suite

    def choose_talon_step_1(self, n, talon):
        """
        Interface method.
        :param n:
        :param talon:
        :return:
        """
        message = "SemiBot.choose_talon_step_1(): "
        piles = 2 if n == 3 else 3 if n == 2 else 6 if n == 1 else 0
        Logs.debug_message(message + "Piles -> " + str(piles))
        scores = [0] * piles
        n_start = 0
        n_end = n
        for pile_index in range(0, piles):
            for n_index in range(n_start, n_end):
                scores[pile_index] += talon[n_index].points
            n_start = n_end
            n_end += n

        return scores.index(max(scores)) * n

    def choose_talon_step_2(self, n, non_disabled_card_indexes):
        """
        Interface method.
        :param n:
        :param non_disabled_card_indexes:
        :return:
        """
        Logs.debug_message("SemiBot.choose_talon_step_2(): " + str(non_disabled_card_indexes))
        return_cards = []
        random_card_indexes = random.sample(set(non_disabled_card_indexes), n)
        for i in random_card_indexes:
            return_cards.append(self.cards[i])
        return return_cards

    def play_card(self, non_disabled_card_indexes, table, suit):
        """
        Interface method.
        :param non_disabled_card_indexes:
        :param table:
        :param suit:
        :return:
        """
        message = "SemiBot.play_card(): "
        if suit == "":
            Logs.debug_message(message + "first one, selecting random card...")
            index = random.sample(set(non_disabled_card_indexes), 1)[0]
            Logs.debug_message(message + "Random card -> " + self.cards[index].alt)
            return self.cards[index]

        if suit != "tarot":
            card = self.play_color(table, suit)
            if card is not None:
                return card
            Logs.debug_message(message + "I probably don't have any colors of suit (" + suit + ") left, going to tarots...")

        return self.play_tarot(table, non_disabled_card_indexes)

    def play_color(self, table, suit):
        # "♥" "♦" "♠" "♣"
        message = "SemiBot.play_color(): "
        tarot_on_desk = False
        card_to_put_down = None
        max_color_on_table = 1
        lowest_color_in_hand = 9
        lcih_index = 0
        for stack in table:
            if table[stack] != "" and not isinstance(table[stack], int):
                color_on_table = int(table[stack][1])
                if suit == table[stack][0] and max_color_on_table < color_on_table:
                    max_color_on_table = color_on_table
            if isinstance(table[stack], int):
                tarot_on_desk = True
        Logs.debug_message(message + "Max Color on table: " + suit + str(max_color_on_table))
        i = 0
        while i < len(self.cards):
            # works only if cards are sorted
            if self.cards[i].is_tarot:
                break
            if self.cards[i].suit == suit:
                if self.cards[i].rank > max_color_on_table and not tarot_on_desk:
                    Logs.debug_message(message + "clicking card -> " + self.cards[i].alt)
                    card_to_put_down = self.cards[i]
                    # del (self.cards[i])
                    break
                if self.cards[i].rank < lowest_color_in_hand:
                    lowest_color_in_hand = self.cards[i].rank
                    lcih_index = i
            i += 1

        if card_to_put_down is None and lowest_color_in_hand != 9:
            Logs.debug_message(message + "clicking lowest color -> " + self.cards[lcih_index].alt)
            card_to_put_down = self.cards[lcih_index]
            # del (self.cards[lcih_index])
            return card_to_put_down
        return card_to_put_down

    def play_tarot(self, table, non_disabled_card_indexes):
        message = "SemiBot.play_tarot(): "
        max_tarot_on_table = 0
        lowest_tarot_in_hand = 22
        ltih_index = 0
        for stack in table:
            if table[stack] != "" and isinstance(table[stack], int) and max_tarot_on_table < table[stack]:
                max_tarot_on_table = table[stack]
        Logs.debug_message(message + "Max Tarot on table: " + str(max_tarot_on_table))
        i = 0
        while i < len(self.cards):
            # works only if cards are sorted
            if self.cards[i].is_tarot:
                if self.cards[i].rank > max_tarot_on_table:
                    Logs.debug_message(message + "clicking card -> " + self.cards[i].alt)
                    card_to_put_down = self.cards[i]
                    # del (self.cards[i])
                    return card_to_put_down
                if lowest_tarot_in_hand > self.cards[i].rank:
                    lowest_tarot_in_hand = self.cards[i].rank
                    ltih_index = i
            i += 1

        if self.check_if_has_tarot_card():
            Logs.debug_message(message + "clicking lowest tarot -> " + self.cards[ltih_index].alt)
            card_to_put_down = self.cards[ltih_index]
            # del (self.cards[ltih_index])
            return card_to_put_down
        Logs.debug_message(message + "I probably don't have any tarots left, selecting random card...")
        ran = random.sample(set(non_disabled_card_indexes), 1)[0]
        Logs.debug_message(message + "Selecting -> " + str(self.cards[ran].alt))
        # del (self.cards[ran])
        return self.cards[ran]

    def check_if_has_tarot_card(self):
        for card in self.cards:
            if card.is_tarot:
                return True
        return False

    def set_suit_helper_objects_and_tarots(self, table):
        """
        Interface method.
        :param table:
        :return:
        """
        return
