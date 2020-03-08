import Configuration
import random
from bot_logic import SuitHelper
from bot_logic import TalonPileHelper
import operator

config = Configuration.Configuration().get_config()
# TODO razširi bazo tako da boš vsak primer (vsak return) si zapisal kolikokrat se je zgodil. npr. z številkami označi in s komentarjem zapiši še kej
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
        # self.color_count = {"♥": 8, "♦": 8, "♠": 8, "♣": 8}
        self.history = {}
        self.ally = "stack0"
        self.suit_objects = {}
        self.candidates = []

    def set_cards(self, cards):
        self.cards = cards

    # TODO prestavi to metodo v Tools.py in uporabi pri ostalih botih
    def init_round(self):
        self.ally = "stack0"
        for s in config["suit_signs"].split(","):
            #if len(self.suit_objects) == 0:
            if s not in self.suit_objects:
                self.suit_objects[s] = SuitHelper.SuitHelper(s)
            else:
                self.suit_objects[s].reset_counters()

        for card in self.cards:
            if card.is_tarot:
                self.tarot_count -= 1
            else:
                if card.is_king:
                    self.suit_objects[card.suit].has_king = True
                self.suit_objects[card.suit].subtract_color()
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
            # XXI mond
            if card.rank == 21:
                has_mond = True
                has_mond_index = i
            # Skis
            if card.rank == 22:
                has_skis = True
                has_skis_index = i
            # I palcka
            if card.rank == 1 and card.is_tarot:
                has_pagat = True
                has_pagat_index = i
            if card.is_king and card.suit == self.playing_suite:
                has_my_color = True
                has_my_color_index = i
            if card.is_tarot:
                self.tarot_count -= 1
            else:
                self.suit_objects[card.suit].subtract_color()
                # self.color_count[card.suit] -= 1

        # Zbiram barvo prej kakor monda ker če z kraljem poberem dobim še XXI zraven
        if has_my_color:
            if has_mond and self.suit_objects[self.playing_suite].color_count < 4:  # self.color_count[self.playing_suite] < 4:
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
                    self.suit_objects[talon_card.suit].color_count -= 1
                    # self.color_count[talon_card.suit] -= 1
            tph.points += points
            tph.grade += grade
            pile_helpers.append(tph)
            n_start = n_end
            n_end += n
        # 0 -> 0; 1 -> 2; 2 -> 4
        # max_grade = (ocena, id oz. index)
        max_grade = (0, 0)
        for ph in pile_helpers:
            if max_grade[0] < ph.grade:
                max_grade = (ph.grade, ph.id)

        # TODO fix this logic
        if self.game == 2:
            # This returns the first card of the pile
            return max_grade[1] * 2
        if self.game == 1:
            return max_grade[1]
        else:
            return max_grade[1]

    def choose_talon_step_2(self, n, non_disabled_card_indexes):
        message = "WonderfulBot.choose_talon_step_2(): "
        suits = config["suit_signs"].split(",")
        tarot_count = 0
        suit_counter = {}
        cards_to_put_down = []
        potential_cards = []

        for suit in suits:
            suit_counter[suit] = SuitHelper.SuitHelper(suit)

        one_card_suits = []
        two_card_suits = []
        other_suits = []

        # preštejem barve
        for card in self.cards:
            if card.is_tarot:
                tarot_count += 1
            else:
                if card.is_king:
                    suit_counter[card.suit].has_king = True
                suit_counter[card.suit].subtract_color()

        # TODO neki nared s tem
        # če si bom mogu taroke zalagat
        if tarot_count + self.game >= len(self.cards):
            pass

        # Zadnji if stavek je zato da ne vključujemo suitov katerih sploh nimamo v roki
        for suit in suit_counter:
            if suit_counter[suit].color_count == 7:
                one_card_suits.append(suit)
            elif suit_counter[suit].color_count == 6:
                two_card_suits.append(suit)
            elif suit_counter[suit].color_count <= 5:
                other_suits.append(suit)

        if len(one_card_suits) > 0:
            print(message + "Suits with 1 card...")
            print(one_card_suits)
            if self.game == 1:
                if len(one_card_suits) == 1:
                    if not suit_counter[one_card_suits[0]].has_king and not self.playing_suite == one_card_suits[0]:
                        return self.get_cards_from_suit(one_card_suits[0])
                else:
                    max_card_rank = 0
                    max_card = None
                    for suit in one_card_suits:
                        suited_cards = self.get_cards_from_suit(suit)
                        for c in suited_cards:
                            if c.rank > max_card_rank and not c.suit == self.playing_suite and not suit_counter[c.suit].has_king:
                                max_card_rank = c.rank
                                max_card = c

                    return [max_card]
            if self.game == 2:
                if len(one_card_suits) == 1:
                    if not suit_counter[one_card_suits[0]].has_king and not self.playing_suite == one_card_suits[0]:
                        cards_to_put_down.append(self.get_cards_from_suit(one_card_suits[0]))
                else:
                    game_2_suits_with_1_card = []
                    for s in one_card_suits:
                        if not suit_counter[s].has_king and not self.playing_suite == s:
                            game_2_suits_with_1_card += self.get_cards_from_suit(s)

                    # TODO raj posortiri po temu kok kart je še ostal oz. vzem v premislek...
                    if len(game_2_suits_with_1_card) > 1:
                        game_2_suits_with_1_card.sort(key=operator.attrgetter('rank'), reverse=True)

                        # Prevermo če so 3je suiti z 1 karto kjer sta druga in tretja karta po ranku enaka
                        if len(game_2_suits_with_1_card) > 2 and \
                                game_2_suits_with_1_card[1].rank == game_2_suits_with_1_card[2].rank and \
                                self.suit_objects[game_2_suits_with_1_card[1].suit] < self.suit_objects[game_2_suits_with_1_card[2].suit]:

                            return [game_2_suits_with_1_card[0], game_2_suits_with_1_card[2]]

                        return game_2_suits_with_1_card[:2]

                    # Doda eno ali nobene karte za založit
                    cards_to_put_down += game_2_suits_with_1_card

        if len(two_card_suits) > 0:
            print(message + "Suits with 2 cards...")
            print(two_card_suits)
            if self.game == 1:
                if self.playing_suite in two_card_suits:
                    ps_list = self.get_cards_from_suit(self.playing_suite)
                    if not ps_list[0].is_king:
                        return [ps_list[0]]
                    return [ps_list[1]]

                # Najprej poiščemo suit, ki se je najmanjkrat pojavil v talonu in v roki.
                suit_with_min_cards = max(suit_counter, key=suit_counter.get)
                swmc_list = self.get_cards_from_suit(suit_with_min_cards)

                # Vrnemo karto, ki ima največ točk in ki ni kralj.
                for c in swmc_list:
                    if not c.is_king:
                        return [c]

            if self.game == 2:
                if len(two_card_suits) == 1:
                    s = two_card_suits[0]
                    two_card_suit_list = self.get_cards_from_suit(s)
                    if not suit_counter[s].has_king:
                        if suit_counter[s].color_count > 3:
                            return two_card_suit_list
                        potential_cards += two_card_suit_list
                    potential_cards.append(two_card_suit_list[1])
                else:
                    suit_points = {}
                    for s in two_card_suits:
                        tcsc_list = self.get_cards_from_suit(s)
                        if not suit_counter[s].has_king:
                            if suit_counter[s].color_count > 3:
                                points = 0
                                for c in tcsc_list:
                                    points += c.points
                                suit_points[s] = points
                            else:
                                potential_cards += tcsc_list
                        else:
                            potential_cards.append(tcsc_list[1])
                    if len(suit_points) != 0:
                        max_points_suit = max(suit_points, key=suit_points.get)
                        print(message + "Suit with max points is: " + max_points_suit)
                        return self.get_cards_from_suit(max_points_suit)

        if len(potential_cards + cards_to_put_down) > 0:
            pass
        else:
            print(message + "No suits with 1 or 2 cards. Choosing cards with max points.")
            sorted_cards = self.cards
            sorted_cards.sort(key=operator.attrgetter('rank'), reverse=True)
            for c in sorted_cards:
                if len(cards_to_put_down) >= self.game:
                    break
                if not c.is_tarot and not c.is_king:
                    cards_to_put_down.append(c)

        return cards_to_put_down

    def get_cards_from_suit(self, suit):
        """
        :param suit: ♥,♦,♠,♣
        :return: List of Card objects reverse sorted by rank.
        """
        suited_cards = []
        for card in self.cards:
            if card.suit == suit:
                suited_cards.append(card)
        suited_cards.sort(key=operator.attrgetter('rank'), reverse=True)
        return suited_cards

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
            if self.cards[i].is_tarot:
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
