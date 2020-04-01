"""
from Configuration import Configuration
from karte.Deck import Deck
import mysql.connector
import operator

Configuration().read_config("../resources/configuration.txt")
config = Configuration().get_config()

mydb = mysql.connector.connect(
    host=config["host"],
    user=config["db_user"],
    passwd=config["db_pass"],
    database=config["database"]
)

try:
    Deck().create_deck("../" + config["tarot_path"])
    ids = Deck().get_random_12_ids()
    cursor = mydb.cursor()

    sql = "INSERT INTO rounds(bot_name, playing, points, tarot_count, color_points, game, talon_located) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = ('Wonderful', 2, 10, 9, 4, 1, 1)
    cursor.execute(sql, values)

    sql = "INSERT INTO RoundCards(round_id, card_id) VALUES (%s, %s)"
    values = []
    last_id = cursor.lastrowid
    for i in ids:
        values.append((last_id, i))
    cursor.executemany(sql, values)
    mydb.commit()
except ValueError:
    print("der is e error")
finally:
    mydb.close()
"""


class RoundCards:
    def __init__(self, round_id, card_ids):
        self.round_id = round_id
        self.card_ids = card_ids

    def get_values(self):
        """
        values = []
        for c_id in self.card_ids:
            values.append((self.round_id, c_id))
        return values
        """
        return [(self.round_id, c_id) for c_id in self.card_ids]
