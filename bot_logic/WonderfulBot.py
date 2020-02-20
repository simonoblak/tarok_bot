import Configuration
import random
from bot_logic import SuitHelper
from bot_logic import TalonPileHelper

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
        self.candidates = []

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
                if card.is_king:
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
                    if self.suit_objects[suit].color_count >= 6:
                        if less_than_3 and self.suit_objects[suit].color_points > self.suit_objects[max_color_points_suit].color_points:
                            max_color_points_suit = suit
                        else:
                            less_than_3 = True
                            max_color_points_suit = suit

                # if removable color is found, select the other one
                if max_color_points_suit != "":
                    suits.remove(max_color_points_suit)
                    print(message + "We can store one color with 2 or less cards: " + suits[0])
                    self.playing_suite = suits[0]
                    return self.playing_suite

                # if no color can be removed, select the color with less cards
                if suit_one.color_count != suit_two.color_count:
                    less_cards_suit = suit_one.suit if suit_one.color_count > suit_two.color_count else suit_two.suit
                    print(message + "minimum cards has: " + less_cards_suit)
                    self.playing_suite = less_cards_suit
                    return self.playing_suite

                # if card number is the same check values; select the higher one
                if suit_one.color_points != suit_two.color_points:
                    higher_points_suit = suit_one.suit if suit_one.color_points > suit_two.color_points else suit_two.suit
                    print(message + "minimum points has: " + higher_points_suit)
                    self.playing_suite = higher_points_suit
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
                if len(two_card_suit + three_card_suit) == 0:
                    ps = one_card_suit
                else:
                    ps = two_card_suit + three_card_suit
                    self.candidates += one_card_suit

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

            # if no color can be removed ...
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
                self.playing_suite = random.choice(three_card_suit)
                print(message + "SOMETHING IS WRONG: " + self.playing_suite)
                return self.playing_suite

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
        pile_helpers = []
        talon_kings = []
        talon_tarots = []
        """
        1. preveri če je klicani kralj v talonu
        2. preveri če je v kupčku kakšna barva enaka kakor klicana barva
        3. od svojih counterjev odštevi ostale karte iz talona
        """

        has_my_color = False
        has_my_color_index = -1
        has_mond = False
        has_mond_index = -1
        has_skis = False
        has_skis_index = -1
        has_pagat = False
        has_pagat_index = -1

        for i, card in enumerate(talon):
            if card.rank == 21:
                has_mond = True
                has_mond_index = i
            if card.rank == 22:
                has_skis = True
                has_skis_index = i
            if card.rank == 1 and card.is_tarot:
                has_pagat = True
                has_pagat_index = i
            if card.is_king and card.suit == self.playing_suite:
                has_my_color = True
                has_my_color_index = i
            if card.is_tarot:
                self.tarot_count -= 1
            else:
                self.color_count[card.suit] -= 1

        # Zbiram barvo prej kakor monda ker če z kraljem poberem dobim še XXI zraven
        if has_my_color:
            if has_mond and self.color_count[self.playing_suite] < 4:
                print(message + "Selecting XXI over the King with my playing suit")
                return has_mond_index

            print(message + "Selecting King with my playing suit...")
            return has_my_color_index

        # Nekak je tole smiselno ker če se zgodi da sta XXI in SKIS v talonu potem se znebis skisa
        if has_mond:
            print(message + "Selecting XXI...")
            return has_mond_index

        if has_skis:
            print(message + "Choosing pile with Skis")
            return has_skis_index

        for i, card in enumerate(talon):
            if card.is_king:
                talon_kings.append((card.suit, i))
            if card.is_tarot:
                talon_tarots.append((card.rank, i))

        # TODO insert logic if talon has kings
        if len(talon_kings) != 0:
            if len(talon_kings) == 1:
                print(message + "Choosing pile with the King")
                return talon_kings[0][1]

            if self.game == 2 and len(talon_kings) == 2:
                """
                Check if 2 kings are in the same pile... this is a hackish way because suming the indexes for game in 2
                0 + 1 = 1; 2 + 3 = 5; 4 + 5 = 10
                """
                index_sum = 0
                for king in talon_kings:
                    index_sum += king[1]
                if index_sum == 1 or index_sum == 5 or index_sum == 10:
                    print(message + "Choosing pile with the 2 Kings")
                    return talon_kings[0][1]

        # Corner case: če se zgodi da ima talon 2 kralja v ločenih kupčkih v igri v 2 potem je 2/3 šanse da bo pagat z enim od kraljev
        if has_pagat:
            print(message + "Selecting I")
            return has_pagat_index

        if len(talon_tarots) != 0:
            pass

        print(message + "Piles -> " + str(piles))
        scores = [0] * piles
        n_start = 0
        n_end = n
        # TODO nared tko da bojo pile helperji pomagal kartam v roki, ne pa zbrat najboljši kupček
        for pile_index in range(piles):
            tph = TalonPileHelper.TalonPileHelper(pile_index, self.game)
            points = 0
            grade = 0
            for n_index in range(n_start, n_end):
                talon_card = talon[n_index]
                # scores[pile_index] += talon_card.points
                points += talon_card.points
                grade += talon_card.points / 2
                if talon_card.is_tarot:
                    grade += talon_card.rank / 10
                    self.tarot_count -= 1
                else:
                    grade += tph.scale_grade_color[talon_card.rank]
                    self.color_count[talon_card.suit] -= 1
            tph.points += points
            tph.grade += grade
            pile_helpers.append(tph)
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
