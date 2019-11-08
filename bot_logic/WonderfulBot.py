from karte import Deck
from karte import Card
import bot_logic.Tools
import Configuration
import random

config = Configuration.Configuration().get_config()


class WonderfulBot:
    def __init__(self, cards):
        # self.deck = Deck.Deck().get_deck()
        self.cards = cards
        self.king_indexes = []
        self.playing_suite = ""
        self.tarot_count = 0
        # "♥" "♦" "♠" "♣"
        self.color_count = {"♥": 0, "♦": 0, "♠": 0, "♣": 0}
        self.history = {}
        self.ally = "stack0"

    def set_cards(self, cards):
        self.cards = cards

    def choose_king(self):

        suits = config["suits"].split(",")
        for card in self.cards:
            if card.name.lower() == "king":
                suits.remove(card.suit)
        self.king_indexes = self.get_king_indexes()
        random_suite = random.choice(suits)
        return random_suite

    def reset_counters(self):
        self.tarot_count = 0
        for c in self.color_count:
            self.color_count[c] = 0
        self.ally = "stack0"

    def choose_talon_step_1(self, n, talon):
        # 3 if self.game == "Tri" else 2 if self.game == "Dve" else 1 if self.game == "Eno" else 0
        # scores = [0] * n
        # for c in talon:

        suits = config["suits"].split(",")
        for card in self.cards:
            if card.name.lower() == "king":
                suits.remove(card.suit)

        return 0

    def choose_talon_step_2(self, n, non_disabled_card_indexes):
        return random.sample(set(non_disabled_card_indexes), n)

    def get_king_indexes(self):
        indexes = []
        for i in range(0, len(self.cards)):
            if self.cards[i].name.lower() == "king":
                indexes.append(i)
        return indexes

    def play_card(self, non_disabled_card_indexes, table, suit):
        message = "SemiBot.play_card(): "
        if suit == "":
            print(message + "first one, selecting random card...")
            index = random.sample(set(non_disabled_card_indexes), 1)[0]
            print(message + " Random card -> " + self.cards[index].alt)
            return index

        if suit != "tarot":
            index = self.play_color(table, suit)
            if index != -1:
                return index
            print(message + "I probably don't have any colors of suit (" + suit + ") left, going to tarots...")

        return self.play_tarot(table, non_disabled_card_indexes)

    def play_color(self, table, suit):
        # "♥" "♦" "♠" "♣"
        message = "SemiBot.play_color(): "
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
            if self.cards[i].alt[0] == suit:
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
        message = "SemiBot.play_tarot(): "
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