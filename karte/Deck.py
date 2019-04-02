from karte import Card


class Deck:
    def __init__(self):
        self.deck = self.create_deck()

    @staticmethod
    def create_deck():
        lines = [line.rstrip('\n') for line in open("resources/tarot_cards.txt")]
        deck = []
        for line in lines:
            name, points, rank, suit = line.split(";")
            card = Card.Card(name, points, rank, suit)
            deck.append(card)
        return deck
