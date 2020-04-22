from Configuration import Configuration
from karte.Deck import Deck
import mysql.connector
import operator

Configuration().read_config("../resources/documents/configuration.txt")
config = Configuration().get_config()

mydb = mysql.connector.connect(
    host=config["host"],
    user=config["db_user"],
    passwd=config["db_pass"],
    database=config["database"]
)

try:
    Deck().create_deck("../" + config["tarot_path"])
    deck = Deck.get_deck()
    deck.sort(key=operator.attrgetter('deck_order'))
    cursor = mydb.cursor()
    sql = "INSERT INTO TarotCards(card_id, card_name, rank, points, suit) VALUES (%s, %s, %s, %s, %s)"
    for card in deck:
        suit = "tarot" if card.suit is None else card.suit
        values = (card.deck_order, card.get_card_name(), card.rank, card.points, suit)
        cursor.execute(sql, values)
    mydb.commit()
except ValueError:
    print("der is e error")
finally:
    mydb.close()
