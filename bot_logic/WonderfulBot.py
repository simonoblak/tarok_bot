import Configuration
import random
from bot_logic import SuitHelper
from bot_logic import TalonPileHelper
import operator
from Logs import Logs
from math import ceil
from players.Player import Player
from bot_logic.AllyWin import AllyWin
from bot_logic.CardRanks import CardRanks
from bot_logic.PlayingStatus import PlayingStatus

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
        self.playing_suite = ""
        self.game = -1
        self.tarot_count = CardRanks.SKIS_INT
        self.history = {}
        self.ally = ""
        self.suit_objects = {}
        self.number_of_rounds = 12 if config["player_number"] == 4 else 16 if config["player_number"] == 3 else 0
        self.important_tarots = [x for x in range(config["min_important_tarot"], 23)]
        self.players = {}
        self.method_outcomes = {"king": -1, "talon1": -1, "talon2": -1}
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
        self.game = -1
        self.tarot_count = CardRanks.SKIS_INT
        self.history = {}
        self.ally = ""
        self.important_tarots = [x for x in range(config["min_important_tarot"], 23)]

        for p in config["player_positions"].split(","):
            self.players[p] = Player(p)
        for s in config["suit_signs"].split(","):
            if s not in self.suit_objects:
                self.suit_objects[s] = SuitHelper.SuitHelper(s)
            else:
                self.suit_objects[s].reset_counters()
                Logs.debug_message("Reseting counters for suit '" + s + "'")

        for card in self.cards:
            if card.is_tarot:
                self.tarot_count -= 1
            else:
                if card.is_king:
                    self.suit_objects[card.suit].has_king = True
                self.suit_objects[card.suit].subtract_color()
                self.suit_objects[card.suit].color_points += card.points
                self.suit_objects[card.suit].card_alts.append(card.alt)

    def choose_king(self):
        """
        Interface method.
        :return:
        """
        # TODO poklič init round na začetku vsake runde, ne pa šele pri choose king
        # self.init_round()

        message = "WonderfulBot.choose_king(): "
        suits = config["suit_signs"].split(",")
        no_king_suits = config["suit_signs"].split(",")

        # Barve, ki nimam v roki oz. imam kralja v tej barvi, izločim iz izbire
        for suit in self.suit_objects:
            if self.suit_objects[suit].has_king:
                Logs.debug_message(message + "Removing suit '" + suit + "' because i have a king")
                no_king_suits.remove(suit)
                suits.remove(suit)
            elif self.suit_objects[suit].color_count == 8:
                Logs.debug_message(message + "Removing suit '" + suit + "' because i don't have that color")
                suits.remove(suit)

        if len(suits) == 0:
            Logs.debug_message(message + "No suit was good. Selecting random...")
            if len(no_king_suits) == 0:
                Logs.warning_message(message + "All 4 kings are in my hand... Good Luck...")
                suits_array = config["suit_signs"].split(",")
            else:
                suits_array = no_king_suits
            self.playing_suite = random.choice(suits_array)
            Logs.debug_message(message + "Randomly selected suit: " + self.playing_suite)
            return self.playing_suite

        if len(suits) == 1:
            Logs.debug_message(message + "Only 1 color is good. Selecting: " + suits[0])
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
                    Logs.debug_message(message + "Appending suit with less than 4 cards: " + suit)
                    suits_with_3_or_less_cards.append(suit)

            if max_suit != "":
                Logs.debug_message(message + "Removing suit with highest point value: " + max_suit)
                suits.remove(max_suit)
                if len(suits) == 1:
                    Logs.debug_message(message + "Only 1 color is good. Selecting: " + suits[0])
                    self.playing_suite = suits[0]
                    return self.playing_suite

            if len(suits_with_3_or_less_cards) == 0:
                Logs.debug_message(message + "Selecting a suit with more than 3 cards: " + lowest_suit)
                self.playing_suite = lowest_suit
                return self.playing_suite

            Logs.debug_message(message + "Still no king... Selecting suit with max color points")
            max_color_points = 0
            max_color_points_suit = ""
            for suit in suits_with_3_or_less_cards:
                if self.suit_objects[suit].color_points > max_color_points:
                    max_color_points = self.suit_objects[suit].color_points
                    max_color_points_suit = suit

            Logs.debug_message(message + "Selecting suit with max color points: " + max_color_points_suit)
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
                    Logs.debug_message(message + "We can store one color with 2 or less cards: " + suits[0])
                    self.playing_suite = suits[0]
                    return self.playing_suite

                # if no color can be removed, select the color with less cards
                if suit_one.color_count != suit_two.color_count:
                    less_cards_suit = suit_one.suit if suit_one.color_count > suit_two.color_count else suit_two.suit
                    Logs.debug_message(message + "minimum cards has: " + less_cards_suit)
                    self.playing_suite = less_cards_suit
                    return self.playing_suite

                # if card number is the same check values; select the higher one
                if suit_one.color_points != suit_two.color_points:
                    higher_points_suit = suit_one.suit if suit_one.color_points > suit_two.color_points else suit_two.suit
                    Logs.debug_message(message + "minimum points has: " + higher_points_suit)
                    self.playing_suite = higher_points_suit
                    return self.playing_suite

                # select random
                self.playing_suite = random.choice(suits)
                Logs.debug_message(message + "randomly selected: " + self.playing_suite)
                return self.playing_suite

            # more than 2 suits
            Logs.debug_message(message + "more than 2 suits available...")
            Logs.debug_message(suits)
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
                Logs.debug_message(message + "minimum cards has: " + min_cards_suit)
                self.playing_suite = min_cards_suit
                return self.playing_suite

            # first check if we can remove 2 colors / if we have two colors with one card
            if len(one_card_suit) >= 2:
                if len(two_card_suit + three_card_suit) == 0:
                    ps = one_card_suit
                else:
                    ps = two_card_suit + three_card_suit

                self.playing_suite = random.choice(ps)
                Logs.debug_message(message + "Selecting random suit that has one card: " + self.playing_suite)
                Logs.debug_message(ps)
                return self.playing_suite

            # check if we can remove a single color
            if len(two_card_suit) >= 1:
                if len(one_card_suit) > 0:
                    # there will be only one suit with one card
                    self.playing_suite = one_card_suit[0]
                    Logs.debug_message(message + "Selecting suit with one card: " + self.playing_suite)
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
                    Logs.debug_message(message + "Selecting suit with max card: " + self.playing_suite)
                    return self.playing_suite

                Logs.error_message("SOMETHING IS WRONG WITH THIS LOGIC. FIX IT IMMEDIATELY!!!")
                self.playing_suite = random.choice(two_card_suit)
                Logs.error_message(message + "SOMETHING IS WRONG: " + self.playing_suite)
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
                    Logs.debug_message(message + "Selecting suit with max card: " + self.playing_suite)
                    return self.playing_suite

                Logs.error_message("SOMETHING IS WRONG WITH THIS LOGIC. FIX IT IMMEDIATELY!!!")
                self.playing_suite = random.choice(three_card_suit)
                Logs.error_message(message + "SOMETHING IS WRONG: " + self.playing_suite)
                return self.playing_suite

        Logs.warning_message(message + "This is not a 1 or 2 game. selecting a random suit with no king...")
        self.playing_suite = random.choice(no_king_suits)
        return self.playing_suite

    def choose_talon_step_1(self, n, talon):
        """
        Interface method.
        :param n:
        :param talon:
        :return:
        """
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
            if card.rank == CardRanks.MOND_INT:
                has_mond = True
                has_mond_index = i
            # Skis
            if card.rank == CardRanks.SKIS_INT:
                has_skis = True
                has_skis_index = i
            # I palcka
            if card.rank == CardRanks.PAGAT_INT and card.is_tarot:
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
                Logs.debug_message(message + "Selecting XXI over the King with my playing suit")
                return has_mond_index

            Logs.debug_message(message + "Selecting King with my playing suit...")
            return has_my_color_index

        # Nekak je tole smiselno ker če se zgodi da sta XXI in SKIS v talonu potem se znebis skisa
        if has_mond:
            Logs.debug_message(message + "Selecting XXI...")
            return has_mond_index

        if has_skis:
            Logs.debug_message(message + "Choosing pile with Skis")
            return has_skis_index

        for i, card in enumerate(talon):
            if card.is_king:
                talon_kings.append((card.suit, i))
            if card.is_tarot:
                talon_tarots.append((card.rank, i))

        # TODO insert logic if talon has kings
        if len(talon_kings) != 0:
            if len(talon_kings) == 1:
                Logs.debug_message(message + "Choosing pile with the King")
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
                    Logs.debug_message(message + "Choosing pile with the 2 Kings")
                    return talon_kings[0][1]

        # Corner case: če se zgodi da ima talon 2 kralja v ločenih kupčkih v igri v 2 potem je 2/3 šanse da bo pagat z enim od kraljev
        if has_pagat:
            Logs.debug_message(message + "Selecting I")
            return has_pagat_index

        # TODO fix this
        if len(talon_tarots) != 0:
            pass

        Logs.debug_message(message + "Piles -> " + str(piles))
        n_start = 0
        n_end = n
        # TODO nared tko da bojo pile helperji pomagal kartam v roki, ne pa zbrat najboljši kupček
        for pile_index in range(piles):
            tph = TalonPileHelper.TalonPileHelper(pile_index, self.game)
            grade = 0
            for n_index in range(n_start, n_end):
                talon_card = talon[n_index]
                # scores[pile_index] += talon_card.points
                # points += talon_card.points
                # grade += talon_card.points / 2
                if talon_card.is_tarot:
                    grade += talon_card.rank / 10
                else:
                    grade += tph.scale_grade_color[talon_card.rank]
            # tph.points += points
            tph.grade += grade
            pile_helpers.append(tph)
            n_start = n_end
            n_end += n
        # 0 -> 0; 1 -> 2; 2 -> 4
        # max_grade = (ocena, id oz. index)
        max_grade = (0, 0)
        Logs.debug_message(message + "Pile grades...")
        for ph in pile_helpers:
            Logs.debug_message(ph.grade)
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
        """
        Interface method.
        :param n:
        :param non_disabled_card_indexes:
        :return:
        """
        message = "WonderfulBot.choose_talon_step_2(): "
        suits = config["suit_signs"].split(",")
        tarot_count = 0
        king_count = 0
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
                    # Kle še enkrat nastavljam v primeru če sem v talonu pobral kralja
                    self.suit_objects[card.suit].has_king = True
                    king_count += 1
                suit_counter[card.suit].subtract_color()

        # TODO neki nared s tem
        # če si bom mogu taroke zalagat
        if tarot_count + king_count >= self.number_of_rounds:
            Logs.debug_message(message + "tarot count and king count are higher than rounds. NICE!!!")
            """
            # in case the 'non_disabled_card_indexes' variable will be removed
            sorted_cards = self.cards
            sorted_cards.sort(key=operator.attrgetter('deck_order'))
            for c in sorted_cards:
                if len(cards_to_put_down) >= self.game:
                    break
                # Deck order 33 je tarok I
                if not c.is_king and c.deck_order != 33:
                    cards_to_put_down.append(c)
            return cards_to_put_down
            """
            for i in non_disabled_card_indexes:
                if len(cards_to_put_down) >= self.game:
                    break
                cards_to_put_down.append(self.cards[i])
            return cards_to_put_down

        # Zadnji if stavek je zato da ne vključujemo suitov katerih sploh nimamo v roki
        for suit in suit_counter:
            if suit_counter[suit].color_count == 7:
                one_card_suits.append(suit)
            elif suit_counter[suit].color_count == 6:
                two_card_suits.append(suit)
            elif suit_counter[suit].color_count <= 5:
                other_suits.append(suit)

        if len(one_card_suits) > 0:
            Logs.debug_message(message + "Suits with 1 card..." + str(one_card_suits))
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
                        cards_to_put_down += self.get_cards_from_suit(one_card_suits[0])
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
            Logs.debug_message(message + "Suits with 2 cards..." + str(two_card_suits))
            if self.game == 1:
                if self.playing_suite in two_card_suits:
                    ps_list = self.get_cards_from_suit(self.playing_suite)
                    if not ps_list[0].is_king:
                        return [ps_list[0]]
                    return [ps_list[1]]

                # Najprej poiščemo suit, ki se je najmanjkrat pojavil v talonu in v roki in ki ga imam v roki
                suit_with_min_cards = 8
                for s in suit_counter:
                    if suit_counter[s].color_count != 8 and suit_counter[s].color_count < suit_with_min_cards:
                        suit_with_min_cards = s
                # suit_with_min_cards = max(suit_counter, key=operator.attrgetter('color_count'))
                swmc_list = self.get_cards_from_suit(suit_with_min_cards)

                # Vrnemo karto, ki ima največ točk in ki ni kralj.
                for c in swmc_list:
                    if not c.is_king:
                        return [c]

            if self.game == 2:
                if len(two_card_suits) == 1:
                    s = two_card_suits[0]
                    two_card_suit_list = self.get_cards_from_suit(s)
                    if self.playing_suite != s:
                        if not suit_counter[s].has_king:
                            if suit_counter[s].color_count > 3:
                                return two_card_suit_list
                            potential_cards += two_card_suit_list
                        else:
                            potential_cards.append(two_card_suit_list[1])
                    else:
                        potential_cards.append(two_card_suit_list[0] if not suit_counter[s].has_king else two_card_suit_list[1])
                else:
                    suit_points = {}
                    for s in two_card_suits:
                        tcsc_list = self.get_cards_from_suit(s)
                        if self.playing_suite != s:
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
                        else:
                            potential_cards.append(tcsc_list[0] if not suit_counter[s].has_king else tcsc_list[1])
                    if len(suit_points) != 0:
                        max_points_suit = max(suit_points, key=suit_points.get)
                        Logs.debug_message(message + "Suit with max points is: " + max_points_suit)
                        return self.get_cards_from_suit(max_points_suit)

        if len(potential_cards) > 0:
            potential_cards.sort(key=operator.attrgetter('rank'), reverse=True)
            for c in potential_cards:
                if len(cards_to_put_down) >= self.game:
                    Logs.debug_message(message + "Enough cards were already selected for this game.")
                    return cards_to_put_down
                cards_to_put_down.append(c)

        Logs.debug_message(message + "No suits with 1 or 2 cards. Choosing cards with max points.")
        sorted_cards = self.cards
        sorted_cards.sort(key=operator.attrgetter('rank'), reverse=True)
        for c in sorted_cards:
            if len(cards_to_put_down) >= self.game:
                break
            # Zadnji pogoj je zato, da nebi podvajali iste karte
            if not c.is_tarot and not c.is_king and c not in potential_cards:
                cards_to_put_down.append(c)

        return cards_to_put_down

    def get_cards_from_suit(self, suit):
        """
        List of Card objects reverse sorted by rank.
        :param suit: ♥,♦,♠,♣
        :return: List of Card objects reverse sorted by rank.
        """
        suited_cards = []
        for card in self.cards:
            if card.suit == suit:
                suited_cards.append(card)
        suited_cards.sort(key=operator.attrgetter('rank'), reverse=True)
        # TODO try this return
        # return [card.suit for card in self.cards if card.suit == suit].sort(key=operator.attrgetter('rank'), reverse=True)
        return suited_cards

    def play_card(self, non_disabled_card_indexes, table, suit, playing_status):
        """
        Interface method.
        :param non_disabled_card_indexes:
        :param table:
        :param suit:
        :return:
        """
        message = "WonderfulBot.play_card(): "
        if self.ally != "":
            self.players[self.ally].is_ally = True
        if suit == "":
            Logs.debug_message(message + "first one, selecting card...")
            return self.play_first(non_disabled_card_indexes, playing_status)

        if suit != "tarot":
            Logs.debug_message("Suit -> " + suit)
            Logs.debug_message("Suit Objects")
            Logs.debug_message(self.suit_objects.keys())
            card_to_put_down = self.play_color(table, suit)
            if card_to_put_down is not None:
                self.suit_objects[suit].was_already_played = True
                return card_to_put_down
            Logs.debug_message(message + "I probably don't have any colors of suit (" + suit + ") left, going to tarots...")

        return self.play_tarot(table, suit)

    def play_first(self, non_disabled_card_indexes, playing_status):
        """
        preveri če imam kralja katerga barva še ni bila igrana, če ga imam ga odigraj

        Če igram igro in imam barvo v kateri igram odigraj najbolj vredno, če ne pa igram najmanj vredno

        poišči če je kakšna barva že bila odigrana in odigraj najnižjo karto v tej barvi (ki ni dama ?!?)

        tarokiranje če je le možno

        odigraj najnižjega taroka

        random med kartami ki niso kralji ali dame

        random
        :param non_disabled_card_indexes:
        :return:
        """
        message = "WonderfulBot.play_first(): "
        # Check if i have a king that it's suit has not been played yet
        for so in self.suit_objects:
            sh = self.suit_objects[so]
            if sh.has_king and not sh.was_already_played and sh.color_count > 3:
                Logs.debug_message(message + "Choosing king -> " + sh.suit + CardRanks.KING)
                return self.get_card_from_alt(sh.suit + CardRanks.KING)

        # Če igram igro in imam barvo v kateri igram odigraj najbolj vredno, če ne pa igram najmanj vredno
        cards_with_playing_suit = self.get_cards_from_suit(self.playing_suite)
        if len(cards_with_playing_suit) > 0:
            sh = self.suit_objects[self.playing_suite]
            if playing_status == PlayingStatus.PLAYING and not sh.was_already_played and sh.color_count > 3:
                Logs.debug_message(message + "Returning highest card with playing suit ")
                return cards_with_playing_suit[0]
            Logs.debug_message(message + "Returning lowest card with playing suit")
            return cards_with_playing_suit[-1]

        # poišči če je kakšna barva že bila odigrana in odigraj najnižjo karto v tej barvi (ki ni dama ali kralj?!?)
        already_played_suits_in_my_hand = []
        for c in self.cards:
            if not c.is_tarot and \
                    c.suit not in already_played_suits_in_my_hand and \
                    self.suit_objects[c.suit].was_already_played and \
                    c.rank >= int(CardRanks.QUEEN):
                already_played_suits_in_my_hand.append(c.suit)

        if len(already_played_suits_in_my_hand) > 0:
            min_color_count = (0, "")
            for s in already_played_suits_in_my_hand:
                cc = len(self.get_cards_from_suit(s))
                if cc > min_color_count[0]:
                    min_color_count = (cc, s)
            Logs.debug_message(message + "Returning color with lowest rank...")
            return self.get_cards_from_suit(min_color_count[1])[-1]

        # deljeno z 3 je zato ker delim z 3 ostalimi igralci. Svoje taroke takoj odštejem že na začetku
        # Zaokrožim navzgor 'ceil()'
        tarots_in_hand_counter = self.count_tarots_in_hand()
        number_of_players_with_tarots = 0
        for player in self.players:
            if self.players[player].has_tarots:
                number_of_players_with_tarots += 1
        if number_of_players_with_tarots != 0:
            Logs.debug_message(
                message + "Tarot count(" + str(self.tarot_count) + ") number of players with tarots(" + str(
                    number_of_players_with_tarots) + ")")
            Logs.debug_message(message + "tarot_count / number_of_players_with_tarots [" + str(
                self.tarot_count / number_of_players_with_tarots) +
                               "] < [" + str(tarots_in_hand_counter) + "] tarots_in_hand_counter = highest tarot")
        if number_of_players_with_tarots == 0 or ceil(
                self.tarot_count / number_of_players_with_tarots) < tarots_in_hand_counter:
            return self.get_highest_or_lowest_tarot("H")

        # random med kartami ki niso kralji ali dame
        platelci_indexi = []
        for index, c in enumerate(self.cards):
            if not c.is_tarot and c.rank <= int(CardRanks.KAVAL):
                platelci_indexi.append(index)
        if len(platelci_indexi) > 0:
            index = random.sample(set(platelci_indexi), 1)[0]
            Logs.debug_message(message + "Selecting random card lower than Queen.")
            return self.cards[index]

        # odigraj najnižjega taroka
        if tarots_in_hand_counter > 0:
            Logs.debug_message(message + "Returning lowest tarot.")
            return self.get_highest_or_lowest_tarot("L")

        index = random.sample(set(non_disabled_card_indexes), 1)[0]
        Logs.debug_message(message + "Random card -> " + self.cards[index].alt)
        return self.cards[index]

    def play_color(self, table, suit):
        """
        ali je znan soigralec?
        yes
            (ali bo on pobral zaenkrat z tarokom) OR
            (ali bo on pobral zaenkrat z kraljem AND counter > 3 AND barva še ni bila igrana) OR
            (ali bo on pobral zaenkrat z barvo AND ali je zadnji na vrsti) OR
            (ima on ali jaz taroke in ostala dva ne)
            yes
                RETURN max rank, low tarot, highest valued

            ali imam jaz možnost pobrat z KRALJEM AND ali je ta barva še ni bila odigrana AND ali je counter > 3 AND ni taroka na mizi
            yes
                RETURN king

            RETURN min rank

        no
            ali ta barva še ni bila odigrana AND ali je counter > 3
            yes
                ali je tarok na mizi
                    ali jaz tudi nimam barve in grem lahko višje
                        RETURN višji tarok kot highest
                    RETURN min rank
                ali imam kralja v tej barvi
                    RETURN king
                ali je to barva v kateri jaz igram
                    RETURN max rank
                če imam v roki suit iz te runde potem odigram najnižjo barvo
                    RETURN min color
                RETURN min tarot
            RETURN min rank, min tarot
        :param table:
        :param suit:
        :return:
        """
        # "♥" "♦" "♠" "♣"
        message = "WonderfulBot.play_color(): "
        tarot_on_desk = False
        max_tarot_on_table = 0
        for stack in table:
            if isinstance(table[stack], int):
                tarot_on_desk = True
                t = int(table[stack])
                if t > max_tarot_on_table:
                    max_tarot_on_table = t
        Logs.debug_message(message + "Max tarot on table: " + str(max_tarot_on_table))

        sh = self.suit_objects[suit]
        # ali je znan soigralec?
        if self.ally != "":
            # (ali bo on pobral zaenkrat z tarokom) OR
            # (ali bo on pobral zaenkrat z kraljem AND counter > 3 AND barva še ni bila igrana) OR
            # (ali bo on pobral zaenkrat z barvo AND ali je zadnji na vrsti) OR
            # (ima on ali jaz taroke in ostala dva ne)
            #     RETURN max rank
            daw, how = self.does_ally_win(table, suit)
            Logs.debug_message(message + "Does ally win(" + daw.__str__() + "); How(" + how + ")")

            aoml, who = self.is_ally_or_me_last(table)
            Logs.debug_message(message + "Ally or me last(" + aoml.__str__() + "); Who(" + who + ")")

            if daw:
                if (how == AllyWin.TAROT) or \
                        (how == AllyWin.KING and sh.color_count > 3 and not sh.was_already_played) or \
                        (how == AllyWin.COLOR and aoml) or \
                        (not self.do_others_have_tarots() and self.does_ally_or_me_have_tarots()):
                    return_card = self.get_highest_or_lowest_color(suit, "H")
                    if return_card is None:
                        Logs.debug_message(message + "no cards with suit(" + suit + "), trying lowest tarot...")
                        return_card = self.get_highest_or_lowest_tarot("L", True)
                    if return_card is None:
                        Logs.debug_message(message + "no tarots, returning most valuable card...")
                        return_card = self.get_most_or_least_valuable_card(True)
                    return return_card
            # ali imam jaz možnost pobrat z KRALJEM AND ali je ta barva še ni bila odigrana AND ali je counter > 3 AND ni taroka na mizi
            #     RETURN king
            if sh.has_king and not sh.was_already_played and sh.color_count > 3 and not tarot_on_desk:
                Logs.debug_message(message + "Choosing king " + suit + " because it was not played yet.")
                return_card = self.get_card_from_alt(suit + CardRanks.KING)
                if return_card is not None:
                    return return_card
                Logs.warning_message(message + "King was maybe allready played?!?")

            # RETURN min rank
            Logs.debug_message(message + "Returning min rank")
            return self.get_highest_or_lowest_color(suit, "L")

        # ali ta barva še ni bila odigrana AND ali je counter > 3
        if not sh.was_already_played and sh.color_count > 3:
            # ali je tarok na mizi
            #     ali jaz tudi nimam barve in grem lahko višje
            #         RETURN višji tarok kot highest
            #     RETURN min rank
            if tarot_on_desk:
                last = table["stack1"] != "" and table["stack2"] != "" and table["stack3"] != ""
                higher_tarot = self.get_next_higher_tarot(max_tarot_on_table, last)
                has_color_suit = False
                for c in self.cards:
                    if c.suit == suit:
                        has_color_suit = True
                Logs.debug_message(message + "Last(" + last.__str__() +
                                   "); Higher tarot(" + higher_tarot.alt +
                                   "); Has color suit(" + has_color_suit.__str__() + ")")
                if not has_color_suit:
                    if higher_tarot is not None:
                        Logs.debug_message(message + "Returning next higher tarot")
                        return higher_tarot
                    Logs.debug_message(message + "Returning lowest tarot because no color suit and can't beat highest tarot")
                    return_card = self.get_highest_or_lowest_tarot("L")
                    if return_card is not None:
                        return return_card
                    Logs.debug_message(message + "returning minimum valued card...")
                    return self.get_most_or_least_valuable_card()

                Logs.debug_message(message + "Returning minimum rank because tarot on desk")
                return self.get_highest_or_lowest_color(suit, "L")

            if sh.has_king:
                Logs.debug_message(message + "Choosing king " + suit + " because it was not played yet and no ally")
                return self.get_card_from_alt(suit + CardRanks.KING)
            if self.playing_suite == suit:
                Logs.debug_message(message + "Choosing highest color because I'm playing in this color")
                return_card = self.get_highest_or_lowest_color(suit, "H")
                if return_card is not None:
                    return return_card

            # če imam v roki suit iz te runde potem odigram najnižjo barvo
            return_card = self.get_highest_or_lowest_color(suit, "L")
            if return_card is not None:
                Logs.debug_message(message + "Choosing lowest color in my hand")
                return return_card

            # Dam najnižjega taroka
            return_card = self.get_highest_or_lowest_tarot("L", True)
            if return_card is not None:
                Logs.debug_message(message + "Returning lowest tarot because color was not played yet")
                return return_card

        Logs.debug_message(message + "Choosing lowest color if it exists")
        return self.get_highest_or_lowest_color(suit, "L")

    def play_tarot(self, table, suit):
        """
        ali sem zadnji na vrsti AND imam 21ko v roki
            RETURN XXI

        ali je znan soigralec?
        yes
            ali on pobere
                ali je njegova karta v important tarots OR ali sem jaz zadnji?
                    RETURN min tarot, highest valued

                RETURN max tarot
        no
            ali barva še ni bila igrana?
                RETURN min tarot

        ali je karta višja od poba na mizi?
            RETURN max tarot

        RETURN min tarot, lowest valued
        :param table:
        :param suit:
        :param non_disabled_card_indexes:
        :return:
        """
        message = "WonderfulBot.play_tarot(): "
        am_i_last = False

        # ali sem zadnji na vrsti AND imam 21ko v roki
        if table["stack1"] != "" and table["stack2"] != "" and table["stack3"] != "":
            # try to return XXI
            am_i_last = True
            possible_mond = self.get_card_from_alt(CardRanks.MOND, True)
            if possible_mond is not None:
                Logs.debug_message(message + "Returning XXI because I'm last.")
                return possible_mond

        # ali je znan soigralec?
        if self.ally != "":
            daw, how = self.does_ally_win(table, suit)
            Logs.debug_message(message + "Does ally win(" + daw.__str__() + "); How(" + how + ")")

            aoml, who = self.is_ally_or_me_last(table)
            Logs.debug_message(message + "Ally or me last(" + aoml.__str__() + "); Who(" + who + ")")

            # ali on pobere
            if daw:
                # ali je njegova karta v important tarots OR ali sem jaz zadnji?
                if table[self.ally] in self.important_tarots or am_i_last:
                    # RETURN min tarot, highest valued
                    Logs.debug_message(message + "Returning min tarot or highest valued card")
                    return_card = self.get_highest_or_lowest_tarot("L", True)
                    if return_card is not None:
                        return return_card
                else:
                    # return max tarot
                    Logs.debug_message(message + "Returning max tarot because ally may not take...")
                    return_card = self.get_highest_or_lowest_tarot("H")
                    if return_card is not None:
                        return return_card
                # if there are no tarots in my hand just return highest valued
                return self.get_most_or_least_valuable_card(True)

        else:
            # ali barva še ni bila igrana?
            if suit != "tarot" and not self.suit_objects[suit].was_already_played:
                # RETURN min tarot
                return_card = self.get_highest_or_lowest_tarot("L")
                if return_card is not None:
                    Logs.debug_message(message + "Returning lowest tarot because color not played yet")
                    return return_card

        # ali je karta višja od poba na mizi
        for stack in table:
            if table[stack] is None or table[stack] == "":
                continue
            if (not isinstance(table[stack], int) and table[stack][1] > CardRanks.BOY) or table[stack] == 1:
                # RETURN max tarot
                return_card = self.get_highest_or_lowest_tarot("H")
                if return_card is not None:
                    Logs.debug_message(message + "Returning highest tarot to pick up valuable cards...")
                    return return_card

        # Return min tarot, lowest valued
        return_card = self.get_highest_or_lowest_tarot("L")
        if return_card is not None:
            Logs.debug_message(message + "Returning min tarot because no conditions were fulfilled")
            return return_card
        Logs.debug_message(message + "Returning lowest valuable card at the end...")
        return self.get_most_or_least_valuable_card()

    def does_ally_win(self, table, suit):
        message = "WonderfulBot.does_ally_win(): "
        if self.ally != "":
            if suit != "tarot":
                if self.does_ally_win_color(table, suit):
                    # Preverim če pobere z kraljem
                    if "8" in table[self.ally]:
                        Logs.debug_message(message + "Ally wins with KING")
                        return True, AllyWin.KING
                    Logs.debug_message(message + "Ally wins with COLOR")
                    return True, AllyWin.COLOR
            if self.does_ally_win_tarot(table):
                Logs.debug_message(message + "Ally wins with TAROT")
                return True, AllyWin.TAROT
            Logs.debug_message(message + "Ally does not win")
        else:
            Logs.warning_message(message + "Ally not known...")
        return False, ""

    def does_ally_win_color(self, table, suit):
        message = "WonderfulBot.does_ally_win_color(): "
        tarot_on_desk = False
        max_color_on_table = 0
        for stack in table:
            if isinstance(table[stack], int):
                tarot_on_desk = True
            elif table[stack] != "":
                color_on_table = int(table[stack][1])
                if suit == table[stack][0] and max_color_on_table < color_on_table:
                    max_color_on_table = color_on_table

        Logs.debug_message(message + "Max Color on table: " + suit + str(max_color_on_table))

        return suit + str(max_color_on_table) == table[self.ally] and not tarot_on_desk

    def does_ally_win_tarot(self, table):
        message = "WonderfulBot.does_ally_win_tarot(): "
        max_tarot = 0
        for stack in table:
            if isinstance(table[stack], int) and max_tarot < table[stack]:
                max_tarot = table[stack]
        Logs.debug_message(message + "Max tarot on table: " + str(max_tarot))
        return max_tarot == table[self.ally]

    def set_suit_helper_objects_and_tarots(self, table, suit_of_table, talon_cards):
        """
        Interface method
        :param table:
        :param suit_of_table:
        :param talon_cards:
        :return:
        """
        message = "WonderfulBot.set_suit_helper_objects(): "
        if talon_cards is not None:
            Logs.debug_message(message + "Here only to subtract talon...")
            for talon_card in talon_cards:
                if talon_card.is_tarot:
                    self.tarot_count -= 1
                else:
                    self.suit_objects[talon_card.suit].subtract_color()
            return
        for stack in table:
            if stack == "stack0":
                continue
            if table[stack] != "":
                self.players[stack].cards.append(table[stack])
                if isinstance(table[stack], int):
                    self.tarot_count -= 1
                    Logs.debug_message(message + "New tarot counter: " + str(self.tarot_count))
                else:
                    suit = table[stack][0]
                    self.suit_objects[suit].subtract_color()
                    Logs.debug_message("SuitHelper New counter for " + suit + " is: " + str(self.suit_objects[suit].color_count))

                    if table[stack][0] != suit_of_table:
                        self.players[stack].has_tarots = False
            else:
                Logs.error_message(message + "table[stack] is empty?!?")
            if table[stack] in self.important_tarots:
                Logs.debug_message(message + "Removing from important tarots -> " + str(table[stack]))
                self.important_tarots.remove(table[stack])

    def get_most_or_least_valuable_card(self, rev=False):
        """
        reverse -> True -> ['♣7', '♣5', '♣2', '♣1'] -> ♣7
        reverse -> False -> ['♣1', '♣2', '♣5', '♣7'] -> ♣1
        :param rev: True for most valuable. False for least valuable
        :return:
        """
        message = "WonderfulBot.get_most_or_least_valuable_card(): "
        Logs.debug_message(message + "Selecting least or most valuable card..." + rev.__str__())
        sorted_cards = self.cards
        sorted_cards.sort(key=operator.attrgetter('rank'), reverse=rev)
        Logs.debug_message(message + "Selecting -> " + str(sorted_cards[0].alt))
        return sorted_cards[0]

    def check_if_has_tarot_card(self):
        for card in self.cards:
            if card.is_tarot:
                return True
        return False

    def get_card_from_alt(self, alt, mond=False):
        message = "WonderfulBot.get_card_from_alt(): "
        for c in self.cards:
            if c.alt == alt:
                return c
        if not mond:
            Logs.error_message(message + "Something is wrong.")
        return None

    def count_tarots_in_hand(self):
        counter = 0
        for c in self.cards:
            if c.is_tarot:
                counter += 1
        return counter

    def get_highest_or_lowest_tarot(self, order="H", palcka=False, mond=False):
        message = "WonderfulBot.get_highest_or_lowest_tarot(): "
        order = order.upper()
        if order != "H" and order != "L":
            Logs.error_message(message + "Wrong order command! Changing to 'H'.")
            order = "H"
        highest_tarot = (0, None)
        lowest_tarot = (23, None)
        is_last_tarot = self.count_tarots_in_hand() == 1

        for c in self.cards:
            if c.is_tarot:
                if order == "L" and c.rank < lowest_tarot[0]:
                    if c.rank == 1 and len(self.cards) > 1:
                        if palcka or len(self.cards) == 2 or is_last_tarot:
                            Logs.debug_message(message + "Returning 'I' because of the penalty for the last round")
                            return c
                    else:
                        lowest_tarot = (c.rank, c)
                elif order == "H" and c.rank > highest_tarot[0]:
                    if c.rank == CardRanks.MOND_INT:
                        if mond or is_last_tarot or CardRanks.SKIS_INT not in self.important_tarots:
                            Logs.debug_message(message + "Returning 'XXI'")
                            return c
                        elif CardRanks.SKIS_INT in self.important_tarots and len(self.cards) > 1:
                            continue
                    else:
                        highest_tarot = (c.rank, c)

        if order == "H":
            return highest_tarot[1]
        return lowest_tarot[1]

    def get_highest_or_lowest_color(self, suit, order="H"):
        message = "WonderfulBot.get_highest_or_lowest_color(): "
        order = order.upper()
        if order != "H" and order != "L":
            Logs.error_message(message + "Wrong order command! Changing to 'H'.")
            order = "H"
        highest_suit = (0, None)
        lowest_suit = (9, None)

        for c in self.cards:
            if c.suit == suit:
                if order == "H" and c.rank > highest_suit[0]:
                    highest_suit = (c.rank, c)
                elif order == "L" and c.rank < lowest_suit[0]:
                    lowest_suit = (c.rank, c)

        if order == "H":
            return highest_suit[1]
        return lowest_suit[1]

    def get_next_higher_tarot(self, rank_to_beat, last):
        message = "WonderfulBot.get_next_higher_tarot(): "
        for c in self.cards:
            if c.is_tarot and c.rank > rank_to_beat:
                if c.rank == CardRanks.MOND_INT:
                    if CardRanks.SKIS_INT not in self.important_tarots or last or self.count_tarots_in_hand() == 1:
                        Logs.debug_message(message + "Found XXI as higher tarot.")
                        return c

                else:
                    Logs.debug_message(message + "Found next higher tarot.")
                    return c
        Logs.debug_message(message + "Could not find next higher tarot...")
        return None

    def do_others_have_tarots(self):
        for playa in self.players:
            if self.players[playa].has_tarots and self.players[playa].name != self.ally:
                return True
        return False

    def does_ally_or_me_have_tarots(self):
        return self.ally != "" and (self.players[self.ally].has_tarots or self.check_if_has_tarot_card())

    def is_ally_or_me_last(self, table):
        if table["stack1"] != "":
            return True, AllyWin.ME
        if (self.ally == "stack1" and table["stack1"] == "" and table["stack2"] != "") or \
                (self.ally == "stack2" and table["stack2"] == "" and table["stack3"] != "") or \
                (self.ally == "stack3" and table["stack1"] == "" and table["stack2"] == "" and table["stack3"] == ""):
            return True, AllyWin.ALLY
        return False, ""
