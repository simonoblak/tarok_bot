import time
from karte import Deck
import Configuration
from players import Table
from SeleniumComponent import Connector

"""
SPLOŠNI ZAPISKI
-   Ker se je v novem pycharmu pokvarila altgr tipka je potreben workaroud
    Ctrl + Shift + A -> pod 'Actions' poišči 'registry' in obkljukaj ključ
    'actionSystem.force.alt.gr'
"""


print("Start...")

# Reading configuration.txt file
Configuration.Configuration().read_config("resources/configuration.txt")
Configuration.Configuration().check_config()
config = Configuration.Configuration().get_config()

# Deck.Deck().shuffle_deck(config["min_cut_shuffle"], config["max_cut_shuffle"],
# config["min_number_of_shuffles"], config["max_number_of_shuffles"])

# Creating a shuffled deck
Deck.Deck().create_deck(config["tarot_path"])
deck = Deck.Deck().get_deck()

url = config["url"]

valat = Connector.Connector(url)
valat.login()
valat.create_game(config["opponent_bot"])
valat.time_util(18, "Main Loop")

# GAME
valat.get_cards()
while True:
    if valat.state == "bid":
        valat.choose_game()
    elif valat.state == "call":
        valat.choose_king()
    elif valat.state == "talon":
        valat.choose_talon()
    elif valat.state == "bonus":
        valat.napoved()
    elif valat.state == "game":
        valat.the_game()
    elif valat.state == "end_game":
        valat.time_util(20, "Waiting for next game")
    valat.time_util(1, "TarokBot(State) -> " + valat.state)



"""
# Creating players and table
table = Table.Table()
table.set_table()
table.deal_cards()

"""

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


print("----------Players Sorted Cards----------")

for playa in table.players:
    playa.sort_cards()
    c = 0
    print(playa.name)
    for car in playa.cards:
        print(str(c) + ". " + car.get_card_name())
        c += 1
for t in table.talon:
    print(t.get_card_name())
print("----------------------------------------")


table.choose_game()
table.choose_king()
table.choose_talon()
"""

# https://en.wikipedia.org/wiki/Tarot_card_games



"""
kaj vsak bot potrebuje?

podatki za vhod v pyquery komponento
	- samo na začetku
		- katere karte imam
		- katero pozicijo imam pri izbiranju talona
		- pod pogojem da sem izbran 
			- pošljem info o izbranem kralju
			- potrebujem info o talonu
			- po možnosti že tam preberem katere karte si lahko založim
		
	- ali sem na vrsti. Lahko je to pogoj, da sploh v naprej kej računa
	
	- katera karta je bila v krogu prva odigrana
	- katere karte so še bile odigrane
	- 
"""