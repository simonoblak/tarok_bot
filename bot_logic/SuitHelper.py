from Logs import Logs

class SuitHelper:
    def __init__(self, suit):
        self.suit = suit
        self.color_count = 8
        self.color_points = 0
        self.card_alts = []
        self.has_king = False
        self.was_already_played = False

    def reset_counters(self):
        self.color_count = 8
        self.color_points = 0
        self.card_alts = []
        self.has_king = False
        self.was_already_played = False

    def subtract_color(self):
        if self.color_count - 1 < 0:
            Logs.error_message("SuitHelper.subtract_color(): Color count for suit(" + self.suit + ") is less than 0 ?!?!")
        self.color_count -= 1
