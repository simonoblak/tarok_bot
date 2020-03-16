import Configuration
from karte import Deck
from bot_logic import RandomBot
from bot_logic import SemiBot
from bot_logic import WonderfulBot
from Logs import Logs
import random


config = Configuration.Configuration().get_config()


class Tools:
    def __init__(self):
        self.deck = Deck.Deck().get_deck()
        self.played_cards = []
        self.position_in_talon = 3
        self.players = []
        self.cards = []
        self.playing_bot = self.create_bot(self.cards)
        self.game = 0
        Logs.init_logs()

    def create_bot(self, cards):
        bot_name = config["playing_bot"]
        Logs.debug_message("Playing bot: " + bot_name)
        if bot_name == "RandomBot":
            return RandomBot.RandomBot(cards)
        elif bot_name == "SemiBot":
            return SemiBot.SemiBot(cards)
        elif bot_name == "WonderfulBot":
            return WonderfulBot.WonderfulBot(cards)

    def is_my_turn(self, times):
        return times[0] != times[1]

    def set_bot_game(self):
        self.playing_bot.game = self.game

    def init_round(self):
        Logs.info_message("Tools.init_round(): initializing and reseting parameters...")
        self.playing_bot.init_round()

    def choose_king(self):
        suite = self.playing_bot.choose_king()
        Logs.info_message("Tools.choose_king(): Suit -> " + suite)
        return suite + "8"

    def choose_talon_step_1(self, online_talon):
        talon = self.convert_alts_to_cards(online_talon)
        index = self.playing_bot.choose_talon_step_1(self.game, talon)
        Logs.info_message("Tools.choose_talon_step_1(): Card alt -> " + str(talon[index].alt))
        return index

    def choose_talon_step_2(self, non_disabled_card_indexes):
        returned_cards = self.playing_bot.choose_talon_step_2(self.game, non_disabled_card_indexes)
        alts_string = ""
        indexes = []
        for returned_card in returned_cards:
            alts_string += returned_card.alt + ", "
            for i, card in enumerate(self.cards):
                if returned_card.alt == card.alt:
                    indexes.append(i)
        Logs.info_message("Tools.choose_talon_step_2(): Alts -> " + alts_string)
        return sorted(indexes, reverse=True)

    def convert_online_cards_into_bot_format(self, online_cards):
        self.playing_bot.cards = self.cards = self.convert_alts_to_cards(online_cards)
        for c in self.cards:
            Logs.debug_message("Tools.convert_online_cards_into_bot_format(): " + c.get_card_name())

    def convert_alts_to_cards(self, online_cards):
        tab = []
        for online_card in online_cards:
            for card in self.deck:
                if online_card == card.alt:
                    tab.append(card)
        return tab

    def set_game(self, game_text):
        self.game = 3 if game_text == "Tri" else 2 if game_text == "Dve" else 1 if game_text == "Ena" else 0

    def play_card(self, non_disabled_card_indexes, table):
        message = "Tools.play_card(): "
        suit = ""
        for player in config["player_positions"].split(","):
            if table[player] != "":
                suit = self.get_suit(table[player])
                break

        card = self.playing_bot.play_card(non_disabled_card_indexes, table, suit)
        if card is None:
            Logs.error_message(message + "Card is None... No card was played")
            return random.sample(set(non_disabled_card_indexes), 1)[0]
        Logs.info_message(message + "Played card is -> " + card.alt)
        for i in range(len(self.cards)):
            if self.cards[i].alt == card.alt:
                return i
        Logs.error_message(message + "Something is WRONG!!!!!!!!!!!!!!!")

    def get_suit(self, alt):
        return "tarot" if isinstance(alt, int) else alt[0]
