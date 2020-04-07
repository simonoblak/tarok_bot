class MethodOutcomes:
    def __init__(self):
        self.round_id = None
        self.bot_name = None
        self.choose_king = None
        self.choose_talon_1 = None
        self.choose_talon_2 = None

    def get_values(self):
        return (self.round_id,
                self.bot_name,
                self.choose_king,
                self.choose_talon_1,
                self.choose_talon_2)
