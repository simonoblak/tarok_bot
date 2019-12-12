import Configuration
import random
from bot_logic import SuitHelper

config = Configuration.Configuration().get_config()

"""
kings
https://snipsave.com/user/blavrhovec/snippet/r09laEtAoDu4GJHFBO/?fbclid=IwAR1q8tiih5H3l-60Um59RbU28vuM0O6ndB4PJUUn-3CfUZgG7exzCyFXseo

izbira iger
https://snipsave.com/user/blavrhovec/snippet/uMFsYBo2XehFsb5Hii/?fbclid=IwAR29y2F0B6yT44Yg0KEhT11RkIJIdtnZk1IU6bVjW81oZCN46HMH-1mQ8VU
"""


class WonderfulBot:
    def __init__(self, cards):
        self.cards = cards
        self.king_indexes = []
        self.playing_suite = ""
        self.game = -1
        self.tarot_count = 22
        # "♥" "♦" "♠" "♣"
        self.color_count = {"♥": 8, "♦": 8, "♠": 8, "♣": 8}
        self.history = {}
        self.ally = "stack0"
        self.suit_objects = {}
        self.candidate_suits = []

    def set_cards(self, cards):
        self.cards = cards

    # TODO prestavi to metodo v Tools.py in uporabi pri ostalih botih
    def init_round(self):
        for s in config["suit_signs"].split(","):
            if len(self.suit_objects) == 0:
                self.suit_objects[s] = SuitHelper.SuitHelper(s)
            else:
                self.suit_objects[s].reset_counters()

        for card in self.cards:
            if card.is_tarot:
                self.tarot_count -= 1
            else:
                if card.rank == 8:
                    self.suit_objects[card.suit].has_king = True
                self.suit_objects[card.suit].color_count -= 1
                self.suit_objects[card.suit].color_points += card.rank
                self.suit_objects[card.suit].card_alts.append(card.alt)

    def choose_king(self):
        self.init_round()

        message = "WonderfulBot.choose_king(): "
        suits = config["suit_signs"].split(",")
        no_king_suits = config["suit_signs"].split(",")

        # Barve, ki nimam v roki oz. imam kralja v tej barvi, izločim iz izbire
        for suit in self.suit_objects:
            if self.suit_objects[suit].has_king:
                no_king_suits.remove(suit)
                suits.remove(suit)
            elif self.suit_objects[suit].color_count == 8:
                suits.remove(suit)

        if len(suits) == 0:
            print(message + "No suit was good. Selecting random...")
            if len(no_king_suits) == 0:
                print(message + "All 4 kings are in my hand... Good Luck...")
                suits_array = config["suit_signs"].split(",")
            else:
                suits_array = no_king_suits
            self.playing_suite = random.choice(suits_array)
            print(message + "Randomly selected suit: " + self.playing_suite)
            return self.playing_suite

        if len(suits) == 1:
            print(message + "Only 1 color is good. Selecting: " + suits[0])
            self.playing_suite = suits[0]
            return self.playing_suite

        # Igra za v Ena
        if self.game == 1:
            # Odstranjujem barvo, ki imajo samo 1 karto z najvišjo vrednostjo
            max_color_value = 0
            max_suit = ""
            suits_with_3_or_less_cards = []
            lowest_color_count = 9
            lowest_suit = ""
            for suit in suits:
                if self.suit_objects[suit].color_count == 7 and self.suit_objects[suit].color_points > max_color_value:
                    max_color_value = self.suit_objects[suit].color_points
                    max_suit = suit
                if self.suit_objects[suit].color_count < lowest_color_count:
                    lowest_color_count = self.suit_objects[suit].color_count
                    lowest_suit = suit

            for suit in no_king_suits:
                if self.suit_objects[suit].color_count > 5:
                    print(message + "Appending suit with less than 4 cards: " + suit)
                    suits_with_3_or_less_cards.append(suit)

            if max_suit != "":
                print(message + "Removing suit with highest point value: " + max_suit)
                suits.remove(max_suit)
                if len(suits) == 1:
                    print(message + "Only 1 color is good. Selecting: " + suits[0])
                    self.playing_suite = suits[0]
                    return self.playing_suite

            if len(suits_with_3_or_less_cards) == 0:
                print(message + "Selecting a suit with more than 3 cards: " + lowest_suit)
                self.playing_suite = lowest_suit
                return self.playing_suite

            print(message + "Still no king... Selecting suit with max color points")
            max_color_points = 0
            max_color_points_suit = ""
            for suit in suits_with_3_or_less_cards:
                if self.suit_objects[suit].color_points > max_color_points:
                    max_color_points = self.suit_objects[suit].color_points
                    max_color_points_suit = suit

            print(message + "Selecting suit with max color points: " + max_color_points_suit)
            self.playing_suite = max_color_points_suit
            return self.playing_suite

        # Igra za v Dve
        elif self.game == 2:
            if len(suits) == 2:
                suit_one = self.suit_objects[suits[0]]
                suit_two = self.suit_objects[suits[1]]
                # can we remove one color
                max_color_points_suit = ""
                less_than_3 = False
                for suit in suits:
                    if self.suit_objects[suit].color_count >= 7:
                        if less_than_3 and self.suit_objects[suit].color_points > self.suit_objects[max_color_points_suit].color_points:
                            max_color_points_suit = suit
                        else:
                            less_than_3 = True
                            max_color_points_suit = suit

                # if removable color is found, select the other one
                if max_color_points_suit != "":
                    print(message + "We can store one color with 2 or less cards: " + max_color_points_suit)
                    self.playing_suite = max_color_points_suit
                    return self.playing_suite

                # if no color can be removed, select the color with less cards
                if suit_one.color_count != suit_two.color_count:
                    less_cards_suit = suit_one.suit if suit_one.color_count > suit_two.color_count else suit_two.suit
                    print(message + "minimum cards has: " + less_cards_suit)
                    self.playing_suite = less_cards_suit
                    return self.playing_suite

                # if card number is the same check values; select the higher one
                if suit_one.color_points != suit_two.color_points:
                    less_points_suit = suit_one.suit if suit_one.color_points > suit_two.color_points else suit_two.suit
                    print(message + "minimum points has: " + less_points_suit)
                    self.playing_suite = less_points_suit
                    return self.playing_suite

                # select random
                self.playing_suite = random.choice(suits)
                print(message + "randomly selected: " + self.playing_suite)
                return self.playing_suite

            # more than 2 suits
            print(message + "more than 2 suits available...")
            one_card_suit = []
            two_card_suit = []
            three_card_suit = []
            min_cards_suit = ""
            min_cards = 0
            for s in suits:
                if self.suit_objects[s].color_count == 7:
                    one_card_suit.append(s)
                elif self.suit_objects[s].color_count == 6:
                    two_card_suit.append(s)
                elif self.suit_objects[s].color_count == 5:
                    three_card_suit.append(s)
                if self.suit_objects[s].color_count > min_cards:
                    min_cards = self.suit_objects[s].color_count
                    min_cards_suit = s

            if len(one_card_suit + two_card_suit + three_card_suit) == 0:
                print(message + "minimum cards has: " + min_cards_suit)
                self.playing_suite = min_cards_suit
                return self.playing_suite

            # first check if we can remove 2 colors / if we have two colors with one card
            if len(one_card_suit) >= 2:
                ps = one_card_suit if len(two_card_suit + three_card_suit) == 0 else two_card_suit + three_card_suit
                self.playing_suite = random.choice(ps)
                print(message + "Selecting random suit that has two or three cards: " + self.playing_suite)
                return self.playing_suite

            # check if we can remove a single color
            if len(two_card_suit) >= 1:
                if len(one_card_suit) > 0:
                    # there will be only one suit with one card
                    self.playing_suite = one_card_suit[0]
                    print(message + "Selecting suit with one ca: " + self.playing_suite)
                    return self.playing_suite

                max_color_card_suit = ""
                max_color_card = 0
                for s in two_card_suit:
                    for card in self.cards:
                        if s == card.suit and card.rank > max_color_card:
                            max_color_card = card.rank
                            max_color_card_suit = s

                # TODO remove this if because this should produce a suit. This if statement is a failsafe
                if max_color_card_suit != "":
                    self.playing_suite = max_color_card_suit
                    print(message + "Selecting suit with max card: " + self.playing_suite)
                    return self.playing_suite

                print("SOMETHING IS WRONG WITH THIS LOGIC. FIX IT IMMEDIATELY!!!")
                self.playing_suite = random.choice(two_card_suit)
                print(message + "SOMETHING IS WRONG: " + self.playing_suite)
                return self.playing_suite

            if len(three_card_suit) >= 1:
                max_color_card_suit = ""
                max_color_card = 0
                for s in three_card_suit:
                    for card in self.cards:
                        if s == card.suit and card.rank > max_color_card:
                            max_color_card = card.rank
                            max_color_card_suit = s

                # TODO remove this if because this should produce a suit. This if statement is a failsafe
                if max_color_card_suit != "":
                    self.playing_suite = max_color_card_suit
                    print(message + "Selecting suit with max card: " + self.playing_suite)
                    return self.playing_suite

                print("SOMETHING IS WRONG WITH THIS LOGIC. FIX IT IMMEDIATELY!!!")
                self.playing_suite = random.choice(two_card_suit)
                print(message + "SOMETHING IS WRONG: " + self.playing_suite)
                return self.playing_suite

            # if no color can be removed ...

        print(message + "This is not a 1 or 2 game. selecting a random suit with no king...")
        self.playing_suite = random.choice(no_king_suits)
        return self.playing_suite

    def reset_counters(self):
        self.tarot_count = 22
        for c in self.color_count:
            self.color_count[c] = 8
        self.ally = "stack0"

    def choose_talon_step_1(self, n, talon):
        message = "WonderfulBot.choose_talon_step_1(): "
        piles = 2 if n == 3 else 3 if n == 2 else 6 if n == 1 else 0
        print(message + "Piles -> " + str(piles))
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
        return random.sample(set(non_disabled_card_indexes), n)

    def play_card(self, non_disabled_card_indexes, table, suit):
        message = "WonderfulBot.play_card(): "
        if suit == "":
            print(message + "first one, selecting random card...")
            index = random.sample(set(non_disabled_card_indexes), 1)[0]
            print(message + "Random card -> " + self.cards[index].alt)
            return index

        if suit != "tarot":
            index = self.play_color(table, suit)
            if index != -1:
                return index
            print(message + "I probably don't have any colors of suit (" + suit + ") left, going to tarots...")

        return self.play_tarot(table, non_disabled_card_indexes)

    def play_color(self, table, suit):
        # "♥" "♦" "♠" "♣"
        message = "WonderfulBot.play_color(): "
        tarot_on_desk = False
        index = -1
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
        print(message + "Max Color on table: " + suit + str(max_color_on_table))
        i = 0
        while i < len(self.cards):
            # works only if cards are sorted
            if self.cards[i].is_tarot:
                break
            if self.cards[i].suit == suit:
                if self.cards[i].rank > max_color_on_table and not tarot_on_desk:
                    print(message + "clicking card -> " + self.cards[i].alt)
                    index = i
                    del (self.cards[index])
                    break
                if self.cards[i].rank < lowest_color_in_hand:
                    lowest_color_in_hand = self.cards[i].rank
                    lcih_index = i
            i += 1

        if index == -1 and lowest_color_in_hand != 9:
            print(message + "clicking lowest color -> " + self.cards[lcih_index].alt)
            del (self.cards[lcih_index])
            return lcih_index

        return index

    def play_tarot(self, table, non_disabled_card_indexes):
        message = "WonderfulBot.play_tarot(): "
        max_tarot_on_table = 0
        lowest_tarot_in_hand = 22
        ltih_index = 0
        for stack in table:
            if table[stack] != "" and isinstance(table[stack], int) and max_tarot_on_table < table[stack]:
                max_tarot_on_table = table[stack]
        print(message + "Max Tarot on table: " + str(max_tarot_on_table))
        i = 0
        while i < len(self.cards):
            # works only if cards are sorted
            if self.cards[i].suit == "tarot":
                if self.cards[i].rank > max_tarot_on_table:
                    print(message + "clicking card -> " + self.cards[i].alt)
                    del (self.cards[i])
                    return i
                if lowest_tarot_in_hand > self.cards[i].rank:
                    lowest_tarot_in_hand = self.cards[i].rank
                    ltih_index = i
            i += 1

        if self.check_if_has_tarot_card():
            print(message + "clicking lowest tarot -> " + self.cards[ltih_index].alt)
            del (self.cards[ltih_index])
            return ltih_index
        print(message + "I probably don't have any tarots left, selecting random card...")
        ran = random.sample(set(non_disabled_card_indexes), 1)[0]
        print(message + "Selecting -> " + str(self.cards[ran]))
        return ran

    def check_if_has_tarot_card(self):
        for card in self.cards:
            if card.is_tarot:
                return True
        return False
