import Configuration
from karte import Deck
from bot_logic import RandomBot
from bot_logic import SemiBot
from bot_logic import WonderfulBot
from Logs import Logs
import random
from DatabaseComponent.Rounds import Rounds
from DatabaseComponent.RoundCards import RoundCards


config = Configuration.Configuration().get_config()


class Tools:
    def __init__(self):
        self.deck = Deck.Deck().get_deck()
        self.played_cards = []
        self.position_in_talon = 3
        self.players = []
        self.cards = []
        self.playing_bot = self.create_bot(self.cards)
        self.game = -1
        self.tarot_count = 0
        self.color_points = 0
        self.rounds_db = Rounds()
        self.roundCards_db = None
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
        self.game = -1
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
                suit = self.get_suit_from_alt(table[player])
                break

        # self.check_for_ally(table)
        card = self.playing_bot.play_card(non_disabled_card_indexes, table, suit)
        if card is None:
            Logs.error_message(message + "Card is None... No card was played... Selecting Random")
            return random.sample(set(non_disabled_card_indexes), 1)[0]
        Logs.info_message(message + "Played card is -> " + card.alt)
        # TODO čekiri za suit_helperje če so že bli odigrane barve in če odštevaš barve in taroke vsako rundo, important_tarots?!?
        for i in range(len(self.cards)):
            if self.cards[i].alt == card.alt:
                return i
        Logs.error_message(message + "Something is WRONG!!!!!!!!!!!!!!!")

    def get_suit_from_alt(self, alt):
        return "tarot" if isinstance(alt, int) else alt[0]

    def set_suit_helper_objects_and_tarots(self, table):
        self.playing_bot.set_suit_helper_objects_and_tarots(table)

    def check_for_ally(self, table):
        # preverim če jaz igram in če ally še ni bil najden
        message = "Tools.check_for_ally(): "
        if self.playing_bot.playing_suite != "" and self.playing_bot.ally != "":
            for stack in table:
                if table[stack] is not None or table[stack] != "":
                    if not isinstance(table[stack], int) and table[stack] == self.playing_bot.playing_suite + "8":
                        Logs.info_message(message + "Found ally -> " + stack)
                        self.playing_bot.ally = stack

    def set_roundCards_db(self, round_id, card_ids):
        self.roundCards_db = RoundCards(round_id, card_ids)

    def get_card_ids(self):
        return [card.deck_order for card in self.cards]

    def set_rounds_db(self, results, playing, talon_located):
        self.rounds_db.bot_name = config["playing_bot"]
        self.rounds_db.playing = playing
        self.rounds_db.points = results["game_points"] + results["game_diff"]
        self.rounds_db.tarot_count = self.tarot_count
        self.rounds_db.color_points = self.color_points
        self.rounds_db.game = self.game
        self.rounds_db.played_suit = self.playing_bot.playing_suite
        self.rounds_db.game_points = results["game_points"]
        self.rounds_db.game_diff = results["game_diff"]
        self.rounds_db.bonuses = results["bonuses"]
        self.rounds_db.talon_located = 1 if talon_located else 0
        self.rounds_db.time_stamp = Logs.get_timestamp()

    def count_tarots_in_hand_and_color_points(self):
        tc = 0
        cp = 0
        for card in self.cards:
            if card.is_tarot:
                tc += 1
            else:
                cp += card.points
        self.tarot_count = tc
        self.color_points = cp
        Logs.debug_message("Tools tarot_count(" + str(self.tarot_count) + "), color_points(" + str(self.color_points) + ")")

    def extract_scores(self, score):
        message = "Tools.extract_scores(): "
        try:
            return int(score)
        except ValueError:
            Logs.warning_message(message + "Extracting points got wrong.")
            return -10000

    def set_ally(self, ally):
        Logs.info_message("Setting ally -> " + ally)
        self.playing_bot.ally = ally

    def is_ally_set(self):
        return self.playing_bot.ally != ""
