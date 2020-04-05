from karte import Deck
import Configuration
from SeleniumComponent import Connector

"""
SPLOŠNI ZAPISKI
-   Ker se je v novem pycharmu pokvarila altgr tipka je potreben workaroud
    Ctrl + Shift + A -> pod 'Actions' poišči 'registry' in obkljukaj ključ
    'actionSystem.force.alt.gr'

-   https://en.wikipedia.org/wiki/Tarot_card_games

-   https://stackoverflow.com/questions/4010322/sort-a-list-of-class-instances-python/4010558
"""

config = Configuration.Configuration().get_config()


def tarok_bot():
    """
    Main loop for the Tarok Bot
    :return:
    """
    # Creating a deck
    Deck.Deck().create_deck(config["tarot_path"])

    url = config["url"]

    valat = Connector.Connector(url)
    valat.login()
    valat.create_game(config["opponent_bot"])
    valat.time_util(18, "Main Loop")

    # GAME
    while True:
        if valat.state == "bid":
            valat.get_cards()
            valat.choose_game()
        elif valat.state == "call":
            valat.choose_king()
        elif valat.state == "talon":
            valat.choose_talon()
            valat.get_cards(True)
        elif valat.state == "bonus":
            valat.napoved()
        elif valat.state == "game":
            valat.the_game()
        elif valat.state == "end_game":
            valat.time_util(config["waiting_for_next_round"], "Waiting for next game")
            valat.state = "bid"
        valat.time_util(1, "TarokBot(State) -> " + valat.state)
