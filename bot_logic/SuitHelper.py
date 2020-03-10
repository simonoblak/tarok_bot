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
        self.color_count -= 1
