import unittest
from bot_logic import WonderfulBot
from karte import Deck
from karte import Card
from Configuration import Configuration
import operator

Configuration().read_config("../resources/documents/configuration.txt")
Configuration().check_config()
config = Configuration().get_config()
Deck.Deck.create_deck("../" + config["tarot_path"])


class TestWonderfulBot(unittest.TestCase):
    def setUp(self):
        self.deck = Deck.Deck.get_deck()
        # ♥, ♦, ♠, ♣
        self.cards = []  # self.get_cards_from_alts(["♠1", "♠4", "♣6", "♣8", "♦7", "♥5", "♥6", "5", "7", "18", "20", "22"])
        self.bot = WonderfulBot.WonderfulBot([])
        self.bot.game = 0
        #self.bot.init_round()
        self.talon = []
        self.chosen_talon = []  # self.get_cards_from_alts(["11", "♠8"])

    def initialize_test(self, cards, talon, selected_talon):
        self.cards = self.get_cards_from_alts(cards)
        self.bot.cards = self.cards
        self.bot.init_round()
        self.bot.game = len(selected_talon)
        self.talon = self.get_cards_from_alts(talon)
        self.chosen_talon = self.get_cards_from_alts(selected_talon)

    def get_cards_from_alts(self, alts):
        card_list = []
        for alt in alts:
            for c in self.deck:
                if c.alt == alt:
                    card_list.append(c)
                    break
        if len(card_list) != len(alts):
            print("Not all cards were found...")
            raise ValueError
        return card_list

    def talon_zalaganje(self):
        self.bot.cards += self.chosen_talon
        self.bot.cards.sort(key=operator.attrgetter('deck_order'))
        returned_cards = self.bot.choose_talon_step_2(2, [])
        alts = []
        for returned_card in returned_cards:
            alts.append(returned_card.alt)

        alts.sort()
        return alts

    def test_case_1(self):
        self.initialize_test(["♠1", "♠4", "♣6", "♣8", "♦7", "♥5", "♥6", "5", "7", "18", "20", "22"],
                             [],
                             ["11", "♠8"])
        # KING
        self.assertEqual(self.bot.choose_king(), "♦")
        # TALON ZALAGANJE
        self.assertEqual(self.talon_zalaganje(), ["♥5", "♥6"])

    def test_case_2(self):
        self.initialize_test(["♣1", "♣6", "♠2", "♠4", "♦3", "♦4", "3", "5", "6", "7", "18", "22"],
                             ["♥2", "♥6", "♣2", "♥7", "14", "♠1"],
                             ["14"])

        # KING
        self.assertEqual(self.bot.choose_king(), "♣")
        # TALON IZBIRA
        self.assertEqual(self.bot.choose_talon_step_1(self.bot.game, self.talon), 4)
        # TALON ZALAGANJE
        self.assertEqual(self.talon_zalaganje(), ["♣6"])

    def test_case_3(self):
        self.initialize_test(["♣2", "♣7", "♥1", "♥3", "♦1", "♦2", "♦6", "♦7", "12", "14", "18", "21"],
                             ["♠5", "9", "♠6", "7", "♠7", "2"],
                             ["♠6", "7"])

        # KING
        s = self.bot.choose_king()
        self.assertEqual(s, "♣")
        # TALON IZBIRA
        self.assertEqual(self.bot.choose_talon_step_1(self.bot.game, self.talon), 2)
        # TALON ZALAGANJE
        self.assertEqual(self.talon_zalaganje(), ["♥1", "♥3"])

    def test_case_4(self):
        self.initialize_test(["♥5", "♠2", "♠3", "♠4", "♠5", "♦5", "7", "9", "11", "13", "17", "20"],
                             ["♦7", "♠6", "♦3", "♣3", "5", "♥1"],
                             ["♦7", "♠6"])

        # KING
        suit = self.bot.choose_king()
        self.assertTrue(suit in ["♦", "♥"])
        # TALON IZBIRA
        self.assertEqual(self.bot.choose_talon_step_1(self.bot.game, self.talon), 0)
        # TALON ZALAGANJE
        cards_to_put_down = ["♦5", "♦7"] if suit == "♥" else ['♥5', '♦7']
        self.assertEqual(self.talon_zalaganje(), cards_to_put_down)

    def test_case_5(self):
        self.initialize_test(["♣8", "♥1", "♥4", "♥5", "♠1", "♠5", "♦1", "3", "4", "9", "17", "20"],
                             ["5", "♠8", "♠2", "♦8", "2", "♦4"],
                             ["♠2", "♦8"])

        # KING
        suit = self.bot.choose_king()
        self.assertEqual(suit, "♦")
        # TALON IZBIRA
        self.assertEqual(self.bot.choose_talon_step_1(self.bot.game, self.talon), 3)
        # TALON ZALAGANJE
        self.assertEqual(self.talon_zalaganje(), ["♥5", "♠5"])

    def test_case_6(self):
        self.initialize_test(["♣7", "♥2", "♥4", "♦2", "8", "11", "12", "13", "14", "18", "20", "22"],
                             ["♦4", "♥7", "♠1", "♠4", "♠2", "♣1"],
                             ["♥7"])

        # KING
        suit = self.bot.choose_king()
        self.assertEqual(suit, "♦")
        # TALON IZBIRA
        self.assertEqual(self.bot.choose_talon_step_1(self.bot.game, self.talon), 1)
        # TALON ZALAGANJE
        self.assertEqual(self.talon_zalaganje(), ["♣7"])

    def test_case_7(self):
        self.initialize_test(["♣6", "♥4", "♥7", "♦5", "♠4", "♠7", "12", "13", "14", "18", "20", "22"],
                             ["1", "♣8", "♦7", "♠3", "♥3", "18"],
                             ["1", "♣8"])

        # KING
        suit = self.bot.choose_king()

        self.assertEqual(suit, "♥")
        # TALON IZBIRA
        self.assertEqual(self.bot.choose_talon_step_1(self.bot.game, self.talon), 1)
        # TALON ZALAGANJE
        self.assertEqual(self.talon_zalaganje(), ["♠4", "♠7"])

    def test_case_8(self):
        self.initialize_test(["♣2", "♣6", "♥6", "♦1", "♠4", "♠5", "12", "13", "14", "18", "20", "22"],
                             ["♦4", "12", "7", "♥2", "5", "♣7"],
                             ["1", "♣8"])

        # KING
        suit = self.bot.choose_king()

        self.assertEqual(suit, "♣")
        # TALON IZBIRA
        self.assertEqual(self.bot.choose_talon_step_1(self.bot.game, self.talon), 1)
        # # TALON ZALAGANJE
        # self.assertEqual(self.talon_zalaganje(), ["♠4", "♠7"])

if __name__ == '__main__':
    unittest.main()
