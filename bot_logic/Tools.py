import Configuration
from karte import Deck
from bot_logic import RandomBot
from bot_logic import SemiBot
from bot_logic import WonderfulBot


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

    def create_bot(self, cards):
        bot_name = config["playing_bot"]
        if bot_name == "RandomBot":
            return RandomBot.RandomBot(cards)
        elif bot_name == "SemiBot":
            return SemiBot.SemiBot(cards)
        elif bot_name == "WonderfulBot":
            return WonderfulBot.WonderfulBot(cards)

    def is_my_turn(self, times):
        return times[0] != times[1]

    def choose_king(self):
        suite = self.playing_bot.choose_king()
        print("Tools.choose_king(): Suit -> " + suite)
        return suite + "8"

    def choose_talon_step_1(self, online_talon):
        talon = self.convert_alts_to_cards(online_talon)
        index = self.playing_bot.choose_talon_step_1(self.game, talon)
        print("Tools.choose_talon(): Index -> " + str(index))
        return index

    def choose_talon_step_2(self, non_disabled_card_indexes):
        return self.playing_bot.choose_talon_step_2(self.game, non_disabled_card_indexes)

    def convert_online_cards_into_bot_format(self, online_cards):
        self.playing_bot.cards = self.cards = self.convert_alts_to_cards(online_cards)
        for c in self.cards:
            print("Tools.convert_online_cards_into_bot_format(): " + c.get_card_name())

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
        suit = ""
        for player in config["player_positions"].split(","):
            if table[player] != "":
                suit = self.get_suit(table[player])
                break

        """
        if table["stack1"] != "":
            suit = self.get_suit(table["stack1"])
        elif table["stack2"] != "":
            suit = self.get_suit(table["stack2"])
        elif table["stack3"] != "":
            suit = self.get_suit(table["stack3"])
        else:
            suit = ""
        """
        return self.playing_bot.play_card(non_disabled_card_indexes, table, suit)

    def get_suit(self, alt):
        return "tarot" if isinstance(alt, int) else alt[0]
