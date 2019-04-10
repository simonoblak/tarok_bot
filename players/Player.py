import operator


class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.radeljc = 0
        self.cards = []

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
