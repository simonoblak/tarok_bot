import Configuration
import random
from bot_logic import SuitHelper

config = Configuration.Configuration().get_config()


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
            self.suit_objects[s] = SuitHelper.SuitHelper(s)

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
        suits = []

        no_king_suits = config["suit_signs"].split(",")
        suit_count = {}
        for card in self.cards:
            if card.is_tarot:
                self.tarot_count -= 1
            else:
                suit = card.suit
                self.color_count[suit] -= 1
                if card.rank == 8:
                    self.suit_objects.pop(suit)
                    no_king_suits.remove(suit)
                else:
                    suit_count[suit] = 1 if suit not in suit_count else suit_count[suit] + 1

        # Barv ki nimam v roki izločim iz izbire
        for suit in suit_count:
            if suit_count[suit] == 8:
                suits.remove(suit)

        if len(suits) == 0:
            print(message + "No suit was good. Selecting random...")
            if len(no_king_suits) == 0:
                print(message + "All 4 kings are in my hand... Good Luck...")
                suits_array = config["suit_signs"].split(",")
            else:
                suits_array = no_king_suits
            self.playing_suite = random.choice(suits_array)
            return self.playing_suite

        if len(suits) == 1:
            print(message + "Only 1 color is good. Selecting: " + suits[0])
            self.playing_suite = suits[0]
            return self.playing_suite

        # Igra za v Ena
        if self.game == 1:
            # Odstranjujemo barve, ki imajo samo 1 karto.
            max_color_value = 0
            for c in self.color_count:
                if self.color_count[c] == 7:
                    pass


        for card in self.cards:
            if not card.is_tarot and card.suit in suits:
                pass

        for suit in suit_count:
            if suit_count[suit] > self.game:
                print(message + "Removing suit(" + suit + ") because suit_count '"
                      + str(suit_count[suit]) + "' > than game '" + str(self.game) + "'")
                suits.remove(suit)

        self.playing_suite = random.choice(suits)
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
