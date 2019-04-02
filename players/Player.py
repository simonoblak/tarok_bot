class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.radeljc = 0
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)
