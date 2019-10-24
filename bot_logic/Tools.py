import Configuration
from players import Player
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
        self.my_turn = False
        self.players = []
        self.cards = []
        self.playing_bot = self.create_bot(self.cards)
        self.game = ""

    def create_bot(self, cards):
        bot_name = config["playing_bot"]
        if bot_name == "RandomBot":
            return RandomBot.RandomBot(cards)
        elif bot_name == "SemiBot":
            return SemiBot.SemiBot(cards)
        elif bot_name == "WonderfulBot":
            return WonderfulBot.WonderfulBot(cards)

    def create_player(self, cards_in_some_format, player_name):  # todo change name for this when in right format
        player = Player.Player(player_name)
        player.cards = cards_in_some_format

    def is_my_turn(self, times):
        self.my_turn = times[0] != times[1]
        return self.my_turn

    def choose_king(self):
        suite = self.playing_bot.choose_king()
        print("Tools.choose_king(): Suit -> " + suite)
        return suite

    def choose_talon_step_1(self, talon):
        """
        if self.game == "Tri":
            index = self.playing_bot.choose_talon_step_1(3, talon)
        elif self.game == "Dve":
            index = self.playing_bot.choose_talon_step_1(2, talon)
        elif self.game == "Eno":
            index = self.playing_bot.choose_talon_step_1(1, talon)
        else:
            # TODO klele je treba še za igro solo brez pohendlat če bo potrebno
            index = 0
        """
        g = 3 if self.game == "Tri" else 2 if self.game == "Dve" else 1 if self.game == "Eno" else 0
        index = self.playing_bot.choose_talon_step_1(g, talon)
        print("Tools.choose_talon(): Index -> " + str(index))
        return index

    def choose_talon_step_2(self, non_disabled_card_indexes):
        """
        if self.game == "Tri":
            return self.playing_bot.choose_talon_step_2(3, non_disabled_card_indexes)
        elif self.game == "Dve":
            return self.playing_bot.choose_talon_step_2(2, non_disabled_card_indexes)
        elif self.game == "Eno":
            return self.playing_bot.choose_talon_step_2(1, non_disabled_card_indexes)
        else:
            return []
        """
        # self.is_tarot = True if "tarot" == suit else False    # value_when_true if condition else value_when_false
        g = 3 if self.game == "Tri" else 2 if self.game == "Dve" else 1 if self.game == "Eno" else 0
        return self.playing_bot.choose_talon_step_2(g, non_disabled_card_indexes)

    def convert_online_cards_into_bot_format(self, online_cards):
        self.cards = []
        for online_card in online_cards:
            for card in self.deck:
                if online_card == card.alt:
                    self.cards.append(card)
        for c in self.cards:
            print("Tools.convert_online_cards_into_bot_format(): " + c.get_card_name())

    def play_card(self, non_disabled_card_indexes):
        return self.playing_bot.play_card(non_disabled_card_indexes)
