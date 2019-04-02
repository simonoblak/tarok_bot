from karte import Deck
import Configuration
from players import Table

print("Start...")

# Reading configuration.txt file
Configuration.Configuration().read_config("resources/configuration.txt")
config = Configuration.Configuration().get_config()

# Creating a shuffled deck
Deck.Deck().create_deck(config["tarot_path"])
Deck.Deck().shuffle_deck(config["min_cut_shuffle"],
                         config["max_cut_shuffle"],
                         config["min_number_of_shuffles"],
                         config["max_number_of_shuffles"])
deck = Deck.Deck().get_deck()

# Creating players and table
table = Table.Table()
table.set_table()
table.deal_cards()

"""
print("----------CARD ORDER----------")
c = 0
for kard in deck:
    print(str(c) + ". " + kard.get_card_name())
    c += 1
print("------------------------------")


print("----------Players Cards----------")

for playa in table.players:
    c = 0
    print(playa.name)
    for car in playa.cards:
        print(str(c) + ". " + car.get_card_name())
        c += 1
for t in table.talon:
    print(t.get_card_name())
print("---------------------------------")

"""
