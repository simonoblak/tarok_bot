import Configuration
from players import Player
from karte import Deck


class Tools:
    def __init__(self):
        self.played_cards = []
        self.position_in_talon = 3
        self.my_turn = False
        self.players = []

    def create_player(self, cards_in_some_format, player_name):  # todo change name for this when in right format
        player = Player.Player(player_name)
        player.cards = cards_in_some_format

    def is_my_turn(self, start_time, end_time):
        self.my_turn = start_time != end_time
