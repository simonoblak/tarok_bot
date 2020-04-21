import Configuration
from karte import Deck
from bot_logic import RandomBot
from bot_logic import SimpleBot
from bot_logic import WonderfulBot
from Logs import Logs
import random
from DatabaseComponent.Rounds import Rounds
from DatabaseComponent.RoundCards import RoundCards
from ProjectConstants.CardRanks import CardRanks
from ProjectConstants.PlayingStatus import PlayingStatus


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
        self.playing_player = ""
        self.not_supported_game = False
        self.selected_talon_alts = []
        self.leaved_talon_alts = []
        self.leaved_talon_ids = []
        self.history_deck = []
        self.talon_points = 0
        self.num_of_colors = 0
        self.king_count = 0
        self.trula_count = 0
        self.rounds_db = Rounds()
        self.roundCards_db = None
        Logs.init_logs()

    def create_bot(self, cards):
        bot_name = config["playing_bot"]
        Logs.debug_message("Playing bot: " + bot_name)
        if bot_name == "RandomBot":
            return RandomBot.RandomBot(cards)
        elif bot_name == "SimpleBot":
            return SimpleBot.SimpleBot(cards)
        elif bot_name == "WonderfulBot":
            return WonderfulBot.WonderfulBot(cards)

    def is_my_turn(self, times):
        return times[0] != times[1]

    def set_bot_game(self):
        self.playing_bot.game = self.game

    def init_round(self):
        Logs.info_message("Tools.init_round(): initializing and resetting parameters...")
        self.game = -1
        self.tarot_count = 0
        self.color_points = 0
        self.suit_of_table = ""
        self.talon_ids = []
        self.put_down_ids = []
        self.playing_status = PlayingStatus.NO
        self.playing_player = ""
        self.not_supported_game = False
        self.selected_talon_alts = []
        self.leaved_talon_alts = []
        self.leaved_talon_ids = []
        self.history_deck = [c.alt for c in self.deck]
        self.talon_points = 0
        self.num_of_colors = 0
        self.king_count = 0
        self.trula_count = 0
        self.rounds_db = Rounds()
        self.roundCards_db = None
        self.playing_bot.init_round()

    def choose_king(self):
        suite = self.playing_bot.choose_king()
        Logs.info_message("Tools.choose_king(): Suit -> " + suite)
        return suite + CardRanks.KING

    def choose_talon_step_1(self, online_talon):
        talon = self.convert_alts_to_cards(online_talon)
        index = self.playing_bot.choose_talon_step_1(self.game, talon)
        Logs.info_message("Tools.choose_talon_step_1(): Card alt -> " + str(talon[index].alt))

        for card in talon:
            if card.alt == self.playing_bot.playing_suite + CardRanks.KING:
                self.playing_status = PlayingStatus.ALONE
        """
        if self.game == 1:
            self.talon_ids.append(talon[index].deck_order)
        elif self.game == 2:
            for i in range(0, 5, 2):
                if i <= index <= i + 1:
                    self.talon_ids.append(talon[i].deck_order)
                    self.talon_ids.append(talon[i + 1].deck_order)
                else:
                    self.talon_points += talon[i].points
        """
        if self.game > 0:
            for i in range(0, 6, self.game):
                if self.game == 2:
                    if i <= index <= i + 1:
                        self.talon_ids.append(talon[i].deck_order)
                        self.talon_ids.append(talon[i + 1].deck_order)
                    else:
                        self.talon_points += talon[i].points + talon[i + 1].points
                        self.leaved_talon_ids.append(talon[i].deck_order)
                        self.leaved_talon_ids.append(talon[i + 1].deck_order)
                elif self.game == 1:
                    if i == index:
                        self.talon_ids.append(talon[i].deck_order)
                    else:
                        self.talon_points += talon[i].points
                        self.leaved_talon_ids.append(talon[i].deck_order)

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
        # return sorted(indexes, reverse=True)
        return alts_tab

    def convert_online_cards_into_bot_format(self, online_cards):
        self.playing_bot.cards = self.cards = self.convert_alts_to_cards(online_cards)
        # for c in self.cards:
        #     Logs.debug_message("Tools.convert_online_cards_into_bot_format(): " + c.get_card_name())

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
        if self.not_supported_game:
            Logs.info_message(message + "NOT SUPPORTED GAME. Returning random non disabled index")
            random_index = random.sample(set(non_disabled_card_indexes), 1)[0]
            card = self.cards[random_index]
            Logs.info_message(message + "Played card is -> " + card.alt)
            return card.alt

        suit = ""
        for player in config["player_positions"].split(","):
            if table[player] != "":
                suit = self.get_suit_from_alt(table[player])
                break

        # self.check_for_ally(table)
        card = self.playing_bot.play_card(non_disabled_card_indexes, table, suit, self.playing_status)
        if card is None:
            Logs.error_message(message + "Card is None... No card was played... Selecting Random")
            random_index = random.sample(set(non_disabled_card_indexes), 1)[0]
            card = self.cards[random_index]
        Logs.info_message(message + "Played card is -> " + card.alt)

        self.suit_of_table = suit if suit != "" else card.suit
        """"
        for i, c in enumerate(self.cards):
            if c.alt == card.alt:
                return i
        Logs.error_message(message + "Something is WRONG!!!!!!!!!!!!!!!")
        """
        return card.alt

    def get_suit_from_alt(self, alt):
        return "tarot" if isinstance(alt, int) else alt[0]

    def set_suit_helper_objects_and_tarots_and_history(self, table, online_talon=None):
        message = "Tools.set_suit_helper_objects_and_tarots_and_history(): "
        talon_cards = None
        if online_talon is not None:
            self.leaved_talon_alts = online_talon
            talon_cards = self.convert_alts_to_cards(online_talon)
            ids = self.get_ids_from_cards(talon_cards)
            for i, c_id in enumerate(ids):
                self.leaved_talon_ids.append(c_id)
                self.talon_points += talon_cards[i].points
                self.remove_from_deck(talon_cards[i].alt)

        if table is None:
            return
        self.playing_bot.set_suit_helper_objects_and_tarots(table, self.suit_of_table, talon_cards)

        for stack in table:
            if table[stack] == "":
                Logs.error_message(message + "table[stack] is empty?!")
                continue
            self.remove_from_deck(str(table[stack]))

    def get_card_ids(self):
        return [card.deck_order for card in self.cards]

    def get_ids_from_cards(self, cards):
        return [c.deck_order for c in cards]

    def get_ids_from_alts(self, alts):
        """
        ids = []
        for alt in alts:
            for card in self.deck:
                if alt == card.alt:
                    ids.append(card.deck_order)
        """

        # return [c.deck_order for alt in alts for c in self.deck if alt == c.alt elif isinstance(alt, int)]
        return [Deck.Deck.alt_to_id[str(alt)] for alt in alts]

    def remove_from_deck(self, alt):
        message = "Tools.remove_from_deck(): "
        if alt in self.history_deck:
            self.history_deck.remove(alt)
            Logs.debug_message(message + "Length of history_deck: " + str(len(self.history_deck)) + "; Removing alt: " + str(alt))
        else:
            Logs.error_message(message + "Element '" + alt + "' does not exist in history_deck")

    def set_roundCards_db(self, round_id, card_ids, stack):
        message = "Tools.set_roundCards_db_list(): "
        c_ids = []
        t_ids = []
        p_ids = []

        if stack == "stack0":
            c_ids = card_ids
            t_ids = self.talon_ids
            p_ids = self.put_down_ids
        elif stack == self.playing_player:
            Logs.debug_message(message + "playing player is: " + self.playing_player)
            c_ids = self.get_ids_from_alts(self.playing_bot.players[stack].cards)
            t_ids = self.get_ids_from_alts(self.selected_talon_alts)

            if len(self.history_deck) == self.game:
                p_ids = self.get_ids_from_alts(self.history_deck)
            else:
                Logs.warning_message(message + "History deck does not match with game(" + str(self.game) + ")!!")
                Logs.warning_message(self.history_deck)
        elif stack == "talon":
            c_ids = self.leaved_talon_ids
        else:
            c_ids = self.get_ids_from_alts(self.playing_bot.players[stack].cards)

        Logs.debug_message(message + "For player(" + stack + ") c_ids: " + str(c_ids))
        Logs.debug_message(message + "For player(" + stack + ") t_ids: " + str(t_ids))
        Logs.debug_message(message + "For player(" + stack + ") p_ids: " + str(p_ids))
        self.roundCards_db = RoundCards(round_id, c_ids, t_ids, p_ids, stack)

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
        if self.playing_bot.ally != "":
            self.rounds_db.ally = self.playing_bot.ally
            self.rounds_db.king_count = self.king_count + self.playing_bot.players[self.playing_bot.ally].king_count
            self.rounds_db.trula_count = self.trula_count + self.playing_bot.players[self.playing_bot.ally].trula_count
        self.rounds_db.talon_points = self.talon_points
        self.rounds_db.num_of_colors = self.num_of_colors
        self.rounds_db.talon_located = 1 if talon_located else 0
        self.rounds_db.time_stamp = Logs.get_timestamp()

    def count_tarots_in_hand_and_color_points(self):
        tc = 0
        cp = 0
        king_count = 0
        trula_count = 0
        for card in self.cards:
            if card.is_tarot:
                tc += 1
                if card.rank == 1 or card.rank == 21 or card.rank == 22:
                    trula_count += 1
            else:
                if card.is_king:
                    king_count += 1
                cp += card.points
        self.tarot_count = tc
        self.color_points = cp
        Logs.debug_message("Tools.count_tarots_in_hand_and_color_points(): tarot_count(" + str(self.tarot_count) + "), color_points(" + str(self.color_points) + ")")

    def count_colors_kings_and_trula(self):
        different_suits = []
        tc = 0
        kc = 0
        for card in self.cards:
            if card.is_tarot:
                if card.rank == 1 or card.rank == 21 or card.rank == 22:
                    tc += 1
            elif card.suit not in different_suits:
                different_suits.append(card.suit)
            if card.is_king:
                kc += 1
        self.trula_count = tc
        self.king_count = kc
        self.num_of_colors = len(different_suits)

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

    def get_playing_suit(self):
        Logs.debug_message("Tools.get_playing_suit(): getting playing suit.")
        return self.playing_bot.playing_suite
