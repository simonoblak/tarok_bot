class Card:
    def __init__(self, name, points, rank, suit, deck_order):
        self.name = name
        self.points = points
        self.rank = rank
        if "tarot" == suit:
            self.is_tarot = True
        else:
            self.is_tarot = False
        self.suit = suit
        self.deck_order = deck_order

    def get_card_name(self):
        if self.is_tarot:
            return self.name
        return self.name + " of " + self.suit
