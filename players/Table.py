import Configuration
from players import Player
from karte import Deck


config = Configuration.Configuration().get_config()


class Table:
    def __init__(self):
        self.player_number = config["player_number"]
        self.number_of_cards = self.get_number_of_cards()
        self.players = []
        self.starting_player = ""
        self.deck = Deck.Deck().get_deck()
        self.talon = []
        self.on_table = []
        self.playing = []
        self.opposing = []

    def get_number_of_cards(self):
        if self.player_number == 4:
            return 12
        elif self.player_number == 3:
            return 16
        return None

    def set_table(self):
        if "player_names" in config:
            player_names = config["player_names"].split(",")
        else:
            player_names = input("Vnesi imena locena z vejico: ").split(",")
        self.starting_player = player_names[0]

        for i in range(len(player_names)):
            self.players.append(Player.Player(player_names[i]))

    def deal_cards(self):
        does_everyone_have_a_tarok_card = True
        while True:
            card_start = 0
            card_end = self.number_of_cards
            for i in range(self.player_number):
                self.players[i].cards = self.deck[card_start:card_end]
                card_end += self.number_of_cards
                card_start += self.number_of_cards
            self.talon = self.deck[-6:]

            for playa in self.players:
                if not playa.check_if_has_tarok_card():
                    does_everyone_have_a_tarok_card = False

            if does_everyone_have_a_tarok_card:
                break

    def split_talon(self, game_index):
        if game_index == 3:
            return [self.talon[:3], self.talon[3:]]
        if game_index == 2:
            return [self.talon[:2], self.talon[2:4], self.talon[4:]]
        if game_index == 1:
            return [self.talon[0], self.talon[1], self.talon[2], self.talon[3], self.talon[4], self.talon[5]]
        return None

    def select_game(self):
        while True:
            if self.starting_player == self.players[0].name:
                print("blable")

