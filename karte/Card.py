class Card:
    def __init__(self, name, points, rank, suit_name, deck_order):
        self.name = name
        self.points = points
        self.rank = rank
        self.is_tarot = "tarot" == suit_name
        self.is_king = not self.is_tarot and self.rank == 8
        self.suit_name = suit_name
        self.suit = self.set_suit()
        self.deck_order = deck_order
        self.alt = str(self.rank) if self.is_tarot else self.suit + str(self.rank)

    def get_card_name(self):
        if self.is_tarot:
            return self.name
        return self.name + " of " + self.suit_name

    def set_suit(self):
        if self.suit_name == "Hearts":
            return "♥"
        elif self.suit_name == "Diamonds":
            return "♦"
        elif self.suit_name == "Spades":
            return "♠"
        elif self.suit_name == "Clubs":
            return "♣"
