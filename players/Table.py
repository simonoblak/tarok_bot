import Configuration
from players import Player
from karte import Deck


config = Configuration.Configuration().get_config()


class Table:
    def __init__(self):
        self.player_number = config["player_number"]
        if self.player_number == 4:
            self.number_of_cards = 12
        elif self.player_number == 3:
            self.number_of_cards = 16
        self.players = []
        self.deck = Deck.Deck().get_deck()
        self.talon = []

    def set_table(self):
        if "player_names" in config:
            player_names = config["player_names"].split(",")
        else:
            player_names = input("Vnesi imena locena z vejico: ").split(",")

        for i in range(len(player_names)):
            self.players.append(Player.Player(player_names[i]))

    def deal_cards(self):
        card_start = 0
        card_end = self.number_of_cards
        for i in range(self.player_number):
            self.players[i].cards = self.deck[card_start:card_end]
            card_end += self.number_of_cards
            card_start += self.number_of_cards
        self.talon = self.deck[-6:]


