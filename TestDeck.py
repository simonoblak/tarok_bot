from karte import Deck
import Configuration

Configuration.Configuration().read_config("resources/configuration.txt")
Configuration.Configuration().check_config()
config = Configuration.Configuration().get_config()

# Creating a deck
Deck.Deck().create_deck(config["tarot_path"])
deck = Deck.Deck()


def do_process():
    m = deck.get_random_12_list_and_talon()

    print("\nCards in hand")
    for index, name in enumerate(m["card_names"]):
        print(str(index + 1) + ". " + name)
    b = input("\nContinue???")
    print("\nTalon")
    for index, name in enumerate(m["talon"]):
        print(str(index + 1) + ". " + name)
