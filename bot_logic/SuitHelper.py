class SuitHelper:
    def __init__(self, suit):
        self.suit = suit
        self.color_count = 8
        self.color_points = 0
        self.card_alts = []
        self.has_king = False

    def reset_counters(self):
        self.color_count = 8
        self.color_points = 0
        self.card_alts = []
        self.has_king = False
