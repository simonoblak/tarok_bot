import unittest
from Configuration import Configuration
from DatabaseComponent.db import Db

Configuration().read_config("../resources/configuration.txt")
Configuration().check_config()
config = Configuration().get_config()


class TestDbData(unittest.TestCase):
    def setUp(self):
        Db.connect_to_db()
        self.min_id = 245

    def test_if_54_rows_for_each_round_in_roundcards(self):
        round_ids = Db.execute_select("SELECT round_id FROM rounds")
        corrupted_ids = []
        for i in round_ids:
            if i[0] < self.min_id:
                continue
            results = Db.execute_select("SELECT count(*) FROM roundcards WHERE round_id = " + str(i[0]))
            print("Testing case for round_id: " + str(i[0]))
            if results[0][0] != 54:
                corrupted_ids.append(i[0])

        print(corrupted_ids)
        self.assertEqual(len(corrupted_ids), 0)

    def tearDown(self):
        Db.close_db()
