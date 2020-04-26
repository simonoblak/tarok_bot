import Configuration
import random
from Logs import Logs
from players.Player import Player
from ProjectConstants.CardRanks import CardRanks
from bot_logic.SuitHelper import SuitHelper
import operator

config = Configuration.Configuration().get_config()


class SimpleBot:
    def __init__(self, cards):
        self.cards = cards
        self.king_indexes = []
        self.playing_suite = ""
        self.game = -1
        self.ally = ""
        self.number_of_rounds = 12 if config["player_number"] == 4 else 16 if config["player_number"] == 3 else 0
        self.players = {}
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
        self.game = -1
        self.ally = ""
        for p in config["player_positions"].split(","):
            self.players[p] = Player(p)

    def choose_king(self):
        """
        Interface method.
        :return:
        """
        message = "SimpleBot.choose_king(): "
        suits = config["suit_signs"].split(",")
        no_king_suits = config["suit_signs"].split(",")
        for card in self.cards:
            if card.is_tarot:
                continue
            if card.is_king:
                Logs.debug_message(message + "Removing suit with king: " + card.suit)
                no_king_suits.remove(card.suit)
            if card.suit in suits:
                Logs.debug_message(message + "Removing suit from my hand: " + card.suit)
                suits.remove(card.suit)

        suit_choice = suits if len(suits) > 0 else no_king_suits
        self.playing_suite = random.choice(suit_choice)
        return self.playing_suite

    def choose_talon_step_1(self, n, talon):
        """
        Interface method.

        Prioritetno izbere kupček, ki vsebuje:
        1. Rufani kralj
        2. Mond
        3. Najvišji tarok
        4. Največ točk
        :param n:
        :param talon:
        :return:
        """
        message = "SimpleBot.choose_talon_step_1(): "
        important_indexes = {"my_king": -1, "mond": -1, "highest_tarot": -1}
        highest_tarot_rank = 0
        for index, card in enumerate(talon):
            if card.alt == self.playing_suite + CardRanks.KING:
                Logs.debug_message(message + "Found my king.")
                important_indexes["my_king"] = index
            if card.rank == CardRanks.MOND_INT:
                Logs.debug_message(message + "Found MOND.")
                important_indexes["mond"] = index
            # if card.rank == CardRanks.SKIS_INT:
            #     Logs.debug_message(message + "Found SKIS.")
            #     important_indexes["skis"] = index
            elif card.is_tarot and card.rank > highest_tarot_rank:
                important_indexes["highest_tarot"] = index
                highest_tarot_rank = card.rank

        for i in important_indexes:
            if important_indexes[i] > -1:
                return important_indexes[i]

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
        message = "SimpleBot.choose_talon_step_2(): "
        suits = config["suit_signs"].split(",")
        tarot_count = 0
        king_count = 0
        suit_counter = {}
        cards_to_put_down = []
        potential_cards = []

        for suit in suits:
            suit_counter[suit] = SuitHelper(suit)

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
                    king_count += 1
                suit_counter[card.suit].subtract_color()

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
                    if not suit_counter[one_card_suits[0]].has_king:  # and not self.playing_suite == one_card_suits[0]:
                        return self.get_cards_from_suit(one_card_suits[0])
                else:
                    max_card_rank = 0
                    max_card = None
                    # max_played_card = None
                    for suit in one_card_suits:
                        suited_cards = self.get_cards_from_suit(suit)
                        for c in suited_cards:
                            if c.rank > max_card_rank and not suit_counter[c.suit].has_king:
                                # if not c.suit == self.playing_suite:
                                max_card_rank = c.rank
                                max_card = c
                                # else:
                                #     max_played_card = c

                    if max_card is not None:
                        return [max_card]

                    # if max_played_card is not None:
                    #     return [max_played_card]
            if self.game == 2:
                if len(one_card_suits) == 1:
                    if not suit_counter[one_card_suits[0]].has_king:  # and not self.playing_suite == one_card_suits[0]:
                        cards_to_put_down += self.get_cards_from_suit(one_card_suits[0])
                else:
                    game_2_suits_with_1_card = []
                    for s in one_card_suits:
                        if not suit_counter[s].has_king:  # and not self.playing_suite == s:
                            game_2_suits_with_1_card += self.get_cards_from_suit(s)

                    if len(game_2_suits_with_1_card) > 1:
                        game_2_suits_with_1_card.sort(key=operator.attrgetter('rank'), reverse=True)
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
                suit_with_min_cards = (8, "")
                for s in suit_counter:
                    if suit_counter[s].color_count != 8 and suit_counter[s].color_count < suit_with_min_cards[0]:
                        suit_with_min_cards = (suit_counter[s].color_count, s)
                # suit_with_min_cards = max(suit_counter, key=operator.attrgetter('color_count'))
                swmc_list = self.get_cards_from_suit(suit_with_min_cards)
                if len(swmc_list) > 0:
                    # Vrnemo karto, ki ima največ točk in ki ni kralj.
                    for c in swmc_list:
                        if not c.is_king:
                            return [c]

            if self.game == 2:
                if len(two_card_suits) == 1:
                    s = two_card_suits[0]
                    two_card_suit_list = self.get_cards_from_suit(s)
                    # if self.playing_suite != s:
                    if not suit_counter[s].has_king:
                        if suit_counter[s].color_count > 3:
                            return two_card_suit_list
                        potential_cards += two_card_suit_list
                    else:
                        potential_cards.append(two_card_suit_list[1])
                    # else:
                    #     potential_cards.append(
                    #         two_card_suit_list[0] if not suit_counter[s].has_king else two_card_suit_list[1])
                else:
                    suit_points = {}
                    for s in two_card_suits:
                        tcsc_list = self.get_cards_from_suit(s)
                        # if self.playing_suite != s:
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
                        # else:
                        #     potential_cards.append(tcsc_list[0] if not suit_counter[s].has_king else tcsc_list[1])
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

    def play_card(self, non_disabled_card_indexes, table, suit, playing_status):
        """
        Interface method.
        :param non_disabled_card_indexes:
        :param table:
        :param suit:
        :return:
        """
        message = "SimpleBot.play_card(): "
        if suit == "":
            Logs.debug_message(message + "first one, selecting least valuable card...")

            sorted_cards = [c for c in self.cards if not c.is_tarot]
            if len(sorted_cards) > 0:
                sorted_cards.sort(key=operator.attrgetter('rank'))
                Logs.debug_message(message + str([c.alt for c in sorted_cards]))
                Logs.debug_message(message + "Selecting -> " + str(sorted_cards[0].alt))
                return sorted_cards[0]

            return self.get_most_or_least_valuable_card()

        if suit != "tarot":
            card = self.play_color(table, suit)
            if card is not None:
                return card
            Logs.debug_message(message + "I probably don't have any colors of suit (" + suit + ") left, going to tarots...")

        return self.play_tarot(table, non_disabled_card_indexes)

    def play_color(self, table, suit):
        # "♥" "♦" "♠" "♣"
        message = "SimpleBot.play_color(): "
        tarot_on_desk = False
        card_to_put_down = None
        max_color_on_table = 1
        lowest_color_in_hand = 9
        lcih_card = 0
        for stack in table:
            if table[stack] != "" and not isinstance(table[stack], int):
                color_on_table = int(table[stack][1])
                if suit == table[stack][0] and max_color_on_table < color_on_table:
                    max_color_on_table = color_on_table
            if isinstance(table[stack], int):
                tarot_on_desk = True
        Logs.debug_message(message + "Max Color on table: " + suit + str(max_color_on_table))

        for card in self.cards:
            # works only if cards are sorted
            if card.is_tarot:
                continue
            if card.suit == suit:
                if card.rank > max_color_on_table and not tarot_on_desk:
                    Logs.debug_message(message + "Found higher ranked card -> " + card.alt)
                    card_to_put_down = card
                    # break
                if card.rank < lowest_color_in_hand:
                    lowest_color_in_hand = card.rank
                    lcih_card = card

        if card_to_put_down is None and lowest_color_in_hand != 9:
            Logs.debug_message(message + "clicking lowest color -> " + lcih_card.alt)
            return lcih_card
        return card_to_put_down

    def play_tarot(self, table, non_disabled_card_indexes):
        message = "SimpleBot.play_tarot(): "
        max_tarot_on_table = 0
        lowest_tarot_in_hand = CardRanks.SKIS_INT + 1
        ltih_card = 0
        for stack in table:
            if table[stack] != "" and isinstance(table[stack], int) and max_tarot_on_table < table[stack]:
                max_tarot_on_table = table[stack]
        Logs.debug_message(message + "Max Tarot on table: " + str(max_tarot_on_table))

        for card in self.cards:
            # works only if cards are sorted
            if card.is_tarot:
                if card.rank > max_tarot_on_table:
                    Logs.debug_message(message + "clicking card -> " + card.alt)
                    return card
                if lowest_tarot_in_hand > card.rank:
                    lowest_tarot_in_hand = card.rank
                    ltih_card = card

        if self.check_if_has_tarot_card():
            Logs.debug_message(message + "clicking lowest tarot -> " + ltih_card.alt)
            return ltih_card

        return self.get_most_or_least_valuable_card()

    def check_if_has_tarot_card(self):
        for card in self.cards:
            if card.is_tarot:
                return True
        return False

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
        return suited_cards

    def get_most_or_least_valuable_card(self, rev=False):
        """
        reverse -> True -> ['♣7', '♣5', '♣2', '♣1'] -> ♣7
        reverse -> False -> ['♣1', '♣2', '♣5', '♣7'] -> ♣1
        :param rev: True for most valuable. False for least valuable
        :return:
        """
        message = "SimpleBot.get_most_or_least_valuable_card(): "
        Logs.debug_message(message + "Selecting least or most valuable card..." + rev.__str__())
        sorted_cards = self.cards
        sorted_cards.sort(key=operator.attrgetter('rank'), reverse=rev)
        Logs.debug_message(message + str([c.alt for c in sorted_cards]))
        Logs.debug_message(message + "Selecting -> " + str(sorted_cards[0].alt))
        return sorted_cards[0]

    def set_suit_helper_objects_and_tarots(self, table, suit_of_table, talon_cards):
        """
        Interface method
        :param table:
        :param suit_of_table:
        :param talon_cards:
        :return:
        """
        message = "SimpleBot.set_suit_helper_objects_and_tarots(): "
        for stack in table:
            if stack == "stack0":
                continue
            if table[stack] != "":
                alt = table[stack]
                self.players[stack].cards.append(alt)
                if isinstance(alt, int):
                    self.players[stack].tarot_count += 1
                    if alt == CardRanks.PAGAT_INT or alt == CardRanks.MOND_INT or alt == CardRanks.SKIS_INT:
                        self.players[stack].trula_count += 1
                    continue
                # od tu naprej so samo barve
                if alt[1] == CardRanks.KING:
                    self.players[stack].king_count += 1
            else:
                Logs.error_message(message + "table[stack] is empty?!?")
