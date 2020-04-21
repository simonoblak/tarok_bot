from karte import Deck
import Configuration
from SeleniumComponent import Connector
import winsound
from CrashWarn.EmailSender import send_email
from CrashWarn.MusicPlayer import MusicPlayer
import traceback
from ProjectConstants.ConnectorState import ConnectorState

"""
SPLOŠNI ZAPISKI
-   Ker se je v novem pycharmu pokvarila altgr tipka je potreben workaroud
    Ctrl + Shift + A -> pod 'Actions' poišči 'registry' in obkljukaj ključ
    'actionSystem.force.alt.gr'

-   https://en.wikipedia.org/wiki/Tarot_card_games

-   https://stackoverflow.com/questions/4010322/sort-a-list-of-class-instances-python/4010558

"""

#TODO
# šola taroka PREČEKIRI!
# https://www.tarok.net/solataroka.php

config = Configuration.Configuration().get_config()


def tarok_bot():
    """
    Main loop for the Tarok Bot
    :return:
    """
    send_email_message = ""
    song_to_play = config["error_song"]
    try:
        # Creating a deck
        Deck.Deck().create_deck(config["tarot_path"])

        url = config["url"]

        valat = Connector.Connector(url)
        valat.login()
        valat.create_game(config["opponent_bot"])
        valat.time_util(18, "Main Loop")

        # GAME
        while True:
            if valat.state == ConnectorState.BID:
                valat.get_cards()
                valat.choose_game()
            elif valat.state == ConnectorState.CALL:
                valat.choose_king()
            elif valat.state == ConnectorState.TALON:
                valat.choose_talon()
            elif valat.state == ConnectorState.BONUS:
                valat.napoved()
            elif valat.state == ConnectorState.GAME:
                valat.the_game()
            elif valat.state == ConnectorState.END_GAME:
                valat.time_util(config["waiting_for_next_round"], "Waiting for next game")
                valat.state = ConnectorState.BID
            elif valat.state == ConnectorState.OVER:
                send_email_message = "Bot has successfully finished testing."
                song_to_play = config["success_song"]
                valat.close_connection()
                break
            valat.time_util(1, "TarokBot(State) -> " + valat.state)
    except KeyError as ke:
        send_email_message = "There was an error. " + str(ke)
        print(traceback.format_exc())
    except IndexError as ie:
        send_email_message = "There was an error. " + str(ie)
        print(traceback.format_exc())
    except TypeError as te:
        send_email_message = "There was an error. " + str(te)
        print(traceback.format_exc())
    except ValueError as ve:
        send_email_message = "There was an error. " + str(ve)
        print(traceback.format_exc())
    except Exception as e:
        send_email_message = "There was an error. " + str(e)
        print(traceback.format_exc())

    send_email(send_email_message)
    MusicPlayer.play_sound(song_to_play)
