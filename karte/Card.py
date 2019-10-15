class Card:
    def __init__(self, name, points, rank, suit, deck_order):
        self.name = name
        self.points = points
        self.rank = rank
        # https://stackoverflow.com/questions/2802726/putting-a-simple-if-then-else-statement-on-one-line
        # self.is_tarot = True if "tarot" == suit else False    # value_when_true if condition else value_when_false
        self.is_tarot = "tarot" == suit
        self.suit = suit
        self.deck_order = deck_order
        self.alt = str(self.rank)

    def get_card_name(self):
        if self.is_tarot:
            return self.name
        return self.name + " of " + self.suit

    def set_alt(self):
        if self.suit == "Hearts":
            self.alt = "♥" + self.alt
        elif self.suit == "Diamonds":
            self.alt = "♦" + self.alt
        elif self.suit == "Clubs":
            self.alt = "♠" + self.alt
        elif self.suit == "Spades":
            self.alt = "♣" + self.alt
