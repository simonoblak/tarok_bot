import operator


class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.radeljc = 0
        self.cards = []
        self.play = "Not decided yet."
        self.available_colors = []
        self.available_tarots = []

    def check_if_has_tarok_card(self):
        for card in self.cards:
            if card.is_tarot:
                return True
        return False

    # Pri klicu metode se vedno IZBRISEJO indexi prejsnega klica!!!!!!!!
    # Preverimo, ce imamo v roki kaksno karto z enako barvo ali ce imamo
    # tarok. Ce nimamo potem vrnemo prazen seznam kar na zunanjem nivoju
    # pomeni da lahko igralec katerokoli karto odigra
    def get_available_cards(self, bottom_card):
        self.available_colors = []
        self.available_tarots = []
        if bottom_card is None:
            return []

        # Preverjanje barve
        for index, card in enumerate(self.cards):
            if card.is_tarot:
                self.available_tarots.append(index)
            elif card.suit == bottom_card.suit:
                self.available_colors.append(index)

        if len(self.available_colors) > 0:
            return self.available_colors
        return self.available_tarots

    def sort_cards(self):
        # https://stackoverflow.com/questions/4010322/sort-a-list-of-class-instances-python/4010558
        self.cards.sort(key=operator.attrgetter('deck_order'))

    def get_cards(self):
        return self.cards

    def remove_card_from_hand(self, index):
        if type(index) is not int and not 0 < index < len(self.cards):
            return False
        del self.cards[index]
        return True
