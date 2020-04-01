class Rounds:
    def __init__(self):
        self.bot_name = None
        self.playing = None
        self.points = None
        self.tarot_count = None
        self.color_points = None
        self.game = None
        self.played_suit = None
        self.game_points = None
        self.game_diff = None
        self.bonuses = None
        self.talon_located = None
        self.time_stamp = None

    def get_values(self):
        return (self.bot_name,
                self.playing,
                self.points,
                self.tarot_count,
                self.color_points,
                self.game,
                self.played_suit,
                self.game_points,
                self.game_diff,
                self.bonuses,
                self.talon_located,
                self.time_stamp)
