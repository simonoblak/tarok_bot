import Configuration
from karte import Deck
from bot_logic import RandomBot
from bot_logic import SemiBot
from bot_logic import WonderfulBot
from Logs import Logs
import random
from DatabaseComponent.Rounds import Rounds
from DatabaseComponent.RoundCards import RoundCards
from DatabaseComponent.MethodOutcomes import MethodOutcomes
from bot_logic.CardRanks import CardRanks
from bot_logic.PlayingStatus import PlayingStatus


config = Configuration.Configuration().get_config()


class Tools:
    def __init__(self):
        self.deck = Deck.Deck().get_deck()
        self.cards = []
        self.playing_bot = self.create_bot(self.cards)
        self.game = -1
        self.tarot_count = 0
        self.color_points = 0
        self.suit_of_table = ""
        self.talon_ids = []
        self.put_down_ids = []
        self.playing_status = PlayingStatus.NO
        self.rounds_db = Rounds()
        self.roundCards_db = None
        self.methodOutcomes_db = MethodOutcomes()
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
        self.tarot_count = 0
        self.color_points = 0
        self.suit_of_table = ""
        self.talon_ids = []
        self.put_down_ids = []
        self.playing_status = PlayingStatus.NO
        self.rounds_db = Rounds()
        self.roundCards_db = None
        self.methodOutcomes_db = MethodOutcomes()
        self.playing_bot.init_round()

    def choose_king(self):
        suite = self.playing_bot.choose_king()
        Logs.info_message("Tools.choose_king(): Suit -> " + suite)
        return suite + "8"

    def choose_talon_step_1(self, online_talon):
        talon = self.convert_alts_to_cards(online_talon)
        index = self.playing_bot.choose_talon_step_1(self.game, talon)
        Logs.info_message("Tools.choose_talon_step_1(): Card alt -> " + str(talon[index].alt))

        for card in talon:
            if card.alt == self.playing_bot.playing_suite + CardRanks.KING:
                self.playing_status = PlayingStatus.ALONE

        if self.game == 1:
            self.talon_ids.append(talon[index].deck_order)
        elif self.game == 2:
            for i in range(0, 5, 2):
                if i <= index <= i + 1:
                    self.talon_ids.append(talon[i].deck_order)
                    self.talon_ids.append(talon[i + 1].deck_order)
            """
            if 0 <= index <= 1:
                talon_ids.append(talon[0].deck_order)
                talon_ids.append(talon[1].deck_order)
            elif 2 <= index <= 3:
                talon_ids.append(talon[2].deck_order)
                talon_ids.append(talon[3].deck_order)
            elif 4 <= index <= 5:
                talon_ids.append(talon[4].deck_order)
                talon_ids.append(talon[5].deck_order)
            """
        return index

    def choose_talon_step_2(self, non_disabled_card_indexes):
        returned_cards = self.playing_bot.choose_talon_step_2(self.game, non_disabled_card_indexes)
        alts_tab = []
        indexes = []
        for returned_card in returned_cards:
            alts_tab.append(returned_card.alt)
            self.put_down_ids.append(returned_card.deck_order)
            for i, card in enumerate(self.cards):
                if returned_card.alt == card.alt:
                    indexes.append(i)
        Logs.info_message("Tools.choose_talon_step_2(): Alts -> " + str(alts_tab))
        return sorted(indexes, reverse=True)

    def convert_online_cards_into_bot_format(self, online_cards):
        self.playing_bot.cards = self.cards = self.convert_alts_to_cards(online_cards)
        # for c in self.cards:
        #     Logs.debug_message("Tools.convert_online_cards_into_bot_format(): " + c.get_card_name())

    def convert_alts_to_cards(self, online_cards):
        # TODO check if this return works
        # return [card for online_card in online_cards for card in self.deck if online_card == card.alt]
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
        card = self.playing_bot.play_card(non_disabled_card_indexes, table, suit, self.playing_status)
        if card is None:
            Logs.error_message(message + "Card is None... No card was played... Selecting Random")
            return random.sample(set(non_disabled_card_indexes), 1)[0]
        Logs.info_message(message + "Played card is -> " + card.alt)

        self.suit_of_table = suit if suit != "" else card.suit

        for i, c in enumerate(self.cards):
            if c.alt == card.alt:
                return i
        Logs.error_message(message + "Something is WRONG!!!!!!!!!!!!!!!")

    def get_suit_from_alt(self, alt):
        return "tarot" if isinstance(alt, int) else alt[0]

    def set_suit_helper_objects_and_tarots(self, table, online_talon=None):
        talon_cards = None
        if online_talon is not None:
            talon_cards = self.convert_alts_to_cards(online_talon)
        self.playing_bot.set_suit_helper_objects_and_tarots(table, self.suit_of_table, talon_cards)

    def get_card_ids(self):
        return [card.deck_order for card in self.cards]

    def set_roundCards_db(self, round_id, card_ids):
        self.roundCards_db = RoundCards(round_id, card_ids, self.talon_ids, self.put_down_ids)

    def set_rounds_db(self, results, talon_located):
        self.rounds_db.bot_name = config["playing_bot"]
        self.rounds_db.playing = self.playing_status
        self.rounds_db.points = results["game_points"] + results["game_diff"]
        self.rounds_db.tarot_count = self.tarot_count
        self.rounds_db.color_points = self.color_points
        self.rounds_db.game = self.game
        self.rounds_db.played_suit = self.playing_bot.playing_suite
        self.rounds_db.game_points = results["game_points"]
        self.rounds_db.game_diff = results["game_diff"]
        self.rounds_db.bonuses = results["bonuses"]
        self.rounds_db.ally = self.playing_bot.ally
        self.rounds_db.talon_located = 1 if talon_located else 0
        self.rounds_db.time_stamp = Logs.get_timestamp()

    def set_methodOutcomes_db(self, round_id):
        self.methodOutcomes_db.round_id = round_id
        self.methodOutcomes_db.bot_name = config["playing_bot"]
        self.methodOutcomes_db.choose_king = self.playing_bot.method_outcomes["king"]
        self.methodOutcomes_db.choose_talon_1 = self.playing_bot.method_outcomes["talon1"]
        self.methodOutcomes_db.choose_talon_2 = self.playing_bot.method_outcomes["talon2"]

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
        Logs.debug_message("Tools.count_tarots_in_hand_and_color_points(): tarot_count(" + str(self.tarot_count) + "), color_points(" + str(self.color_points) + ")")

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

    def set_playing_status(self, status):
        Logs.info_message("Tools.set_playing_status(): Setting playing status to: " + status)
        self.playing_status = status

    def set_playing_suit(self, suit):
        Logs.info_message("Tools.set_playing_suit(): Setting playing suit to: " + suit)
        self.playing_bot.playing_suite = suit
