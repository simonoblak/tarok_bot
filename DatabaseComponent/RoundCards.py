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
from Logs import Logs

class RoundCards:
    def __init__(self, round_id, card_ids, talon_ids, put_down_ids):
        self.round_id = round_id
        self.card_ids = card_ids
        self.talon_ids = talon_ids
        self.put_down_ids = put_down_ids

    def get_values(self):
        if len(self.talon_ids) == 0 and len(self.put_down_ids) == 0:
            return [(self.round_id, c_id, 0, 0) for c_id in self.card_ids]
        values = []
        card_and_talon_ids = self.card_ids + self.talon_ids
        for c_id in card_and_talon_ids:
            t_id = 1 if c_id in self.talon_ids else 0
            p_id = 1 if c_id in self.put_down_ids else 0
            values.append((self.round_id, c_id, t_id, p_id))
        Logs.debug_message("RoundCards.get_values(): Printing values of RoundCards")
        Logs.debug_message(values)
        return values
