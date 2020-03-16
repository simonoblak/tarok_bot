from karte import Card
import random
import operator


class Deck:
    deck = []

    @staticmethod
    def create_deck(path):
        create_deck_message = "Deck.create_deck()"
        print("Creating deck of tarot cards: " + create_deck_message)
        lines = [line.rstrip('\n') for line in open(path)]
        for line in lines:
            name, points, rank, suit, deck_order = line.split(";")
            card = Card.Card(name, int(points), int(rank), suit, deck_order)
            Deck.deck.append(card)
        print("Created deck in: " + create_deck_message)

    @staticmethod
    def get_deck():
        return Deck.deck

    def get_random_12_list_and_talon(self):
        """
        For testing purposes
        :return: map of "cards", "card_names", "talon"
        """
        cards = []
        talon = []
        card_names = []
        m = {}
        numbers = []
        i = 0
        while i < 18:
            ran = random.randint(0, 53)
            if ran not in numbers:
                numbers.append(ran)
                if i < 12:
                    cards.append(self.deck[ran])
                else:
                    talon.append(self.deck[ran].get_card_name())
                i += 1
        cards.sort(key=operator.attrgetter('deck_order'))
        for card in cards:
            card_names.append(card.get_card_name())
        m["cards"] = cards
        m["card_names"] = card_names
        m["talon"] = talon
        return m
