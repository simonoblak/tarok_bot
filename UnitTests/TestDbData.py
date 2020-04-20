import unittest
from Configuration import Configuration
from DatabaseComponent.db import Db

Configuration().read_config("../resources/configuration.txt")
Configuration().check_config()
config = Configuration().get_config()


class TestDbData(unittest.TestCase):
    def setUp(self):
        Db.connect_to_db()
        self.min_id = 425

    def test_if_54_rows_for_each_round_in_roundcards(self):
        round_ids = Db.execute_select("SELECT round_id FROM rounds WHERE round_id > " + str(self.min_id))
        corrupted_ids = []
        for i in round_ids:
            results = Db.execute_select("SELECT count(*) FROM roundcards WHERE round_id = " + str(i[0]))
            print("Testing case for round_id: " + str(i[0]))
            if results[0][0] != 54:
                corrupted_ids.append(i[0])

        print(corrupted_ids)
        self.assertEqual(len(corrupted_ids), 0)

    def tearDown(self):
        Db.close_db()
