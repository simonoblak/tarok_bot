import time
import bot_logic.Tools
import Configuration
import base64
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from Logs import Logs
from DatabaseComponent.db import Db
from AdminComponent.Admin import Admin

config = Configuration.Configuration().get_config()

"""
NOTES
https://selenium-python.readthedocs.io/installation.html

https://stackoverflow.com/a/51534196/11189926

https://stackoverflow.com/questions/45347675/make-selenium-wait-10-seconds

set_page_load_timeout - Sets the amount of time to wait for a page load to complete before throwing an error. If the timeout is negative, page loads can be indefinite.

implicitly_wait - Specifies the amount of time the driver should wait when searching for an element if it is not immediately present.

set_script_timeout - Sets the amount of time to wait for an asynchronous script to finish execution before throwing an error. If the timeout is negative, then the script will be allowed to run indefinitely.
"""


class Connector:
    def __init__(self, url):
        self.url = url
        self.driver = self.init_driver()
        self.wait = WebDriverWait(self.driver, 7)
        self.is_four_players = config["player_number"] == 4
        self.player_name = ""
        self.tool = bot_logic.Tools.Tools()
        self.my_bot_playing = False
        self.rufan = False
        self.talon_located = False
        self.state = "bid"
        self.online_cards = []
        self.card_ids = []
        self.admin_pause = "set"
        self.admin = Admin()
        Logs.init_logs()

    def init_driver(self):
        init_driver_message = "Connector.init_driver()"
        Logs.info_message("Initialising driver for '" + self.url + "': " + init_driver_message)
        # Disabling notifications from web pages
        options_for_chrome = webdriver.ChromeOptions()
        options_for_chrome.add_argument("--disable-notifications")

        # Open chrome and set needed parameters
        web_driver = webdriver.Chrome(options=options_for_chrome)
        web_driver.maximize_window()
        web_driver.get(self.url)
        web_driver.implicitly_wait(5)
        Logs.info_message("Finished: " + init_driver_message)
        return web_driver

    def click_execute(self, element):
        Logs.debug_message("Connector.click_execute: " + element.text)
        self.driver.execute_script("arguments[0].click();", element)

    def add_bots(self, bot, number_of_players):
        for i in range(1, number_of_players):
            self.click_execute(bot)

    def login(self):
        user_config = [line.rstrip('\n') for line in open(config["user_config"])]

        # Set username by email of the player
        self.player_name = user_config[0].split("@")[0]

        # Find the google account login
        google_registration = self.driver.find_element_by_css_selector("a[class='go']")
        self.click_execute(google_registration)

        # Login to google account
        username_input = self.driver.find_element_by_id("identifierId")
        username_input.send_keys(user_config[0] + Keys.ENTER)
        self.driver.implicitly_wait(5)

        if config["is_pass_encoded"] == "yes":
            pw = str(base64.b64decode(user_config[1]), "utf-8")
        else:
            pw = user_config[1]
        pw_input = self.driver.find_element_by_css_selector("input[name='password']")
        pw_input.send_keys(pw + Keys.ENTER)
        self.driver.implicitly_wait(5)

    def create_game(self, opponent_bot):
        create_game_message = "Connector.create_game()"
        Logs.info_message("Creating game: " + create_game_message)

        try:
            # Create new game
            self.time_util(config["time_to_wait"], "pred klikom za novo igro")
            self.driver.implicitly_wait(3)
            create_new_game = self.driver.find_element_by_id("new")
            self.click_execute(create_new_game)

            if not self.is_four_players:
                set_for_three_players = self.driver\
                    .find_element_by_css_selector("div[class='seats']")\
                    .find_element_by_id("seats3")

                self.click_execute(set_for_three_players)

            self.time_util(2, "Pred ustvarjanjem igre")

            self.driver.implicitly_wait(3)
            speed = self.driver.find_element_by_css_selector("input[name='rounds']")
            for i in range(2):
                speed.send_keys(Keys.LEFT)

            self.driver.implicitly_wait(3)
            speed = self.driver.find_element_by_css_selector("input[name='tempo']")
            for i in range(5):
                speed.send_keys(Keys.RIGHT)

            create_game = self.driver.find_element_by_css_selector("input[name='create']")
            self.click_execute(create_game)

            bot_difficulty = self.driver.find_element_by_class_name("ai").find_elements_by_css_selector("span")
            for bot in bot_difficulty:
                if opponent_bot == bot.text:
                    self.add_bots(bot, config["player_number"])
                    break

        except NoSuchElementException:
            Logs.error_message("No element found in: " + create_game_message)
            raise NoSuchElementException

    def get_cards(self, prepare_ids=False):
        get_cards_message = "Connector.get_cards(): "
        Logs.debug_message(get_cards_message + "Getting cards...")

        alts = []
        try:
            self.online_cards = self.driver.find_element_by_id("cards").find_elements_by_css_selector("img")
            for online_card in self.online_cards:
                alt = online_card.get_attribute("alt")
                alts.append(alt)
                Logs.debug_message(get_cards_message + "Added -> " + alt)
        except NoSuchElementException:
            Logs.error_message("No element found in: " + get_cards_message)
            raise NoSuchElementException

        self.tool.convert_online_cards_into_bot_format(alts)
        if prepare_ids:
            self.card_ids = self.tool.get_card_ids()
            self.tool.count_tarots_in_hand_and_color_points()

    def choose_game(self):
        choose_game_message = "Connector.choose_game(): "
        Logs.debug_message(choose_game_message + "Choosing game")
        state_name = "bid"
        self.my_bot_playing = False
        self.tool.init_round()

        while True:
            my_turn = self.tool.is_my_turn(self.get_timers(1))
            Logs.debug_message(choose_game_message + "tool.is_my_turn -> " + str(my_turn))
            if my_turn:
                break
            else:
                self.time_util(1, choose_game_message)

        choose_over = False
        try:
            not_allowed_games = config["not_allowed_games"].split(",")

            while True:
                game_elements = self.driver.find_element_by_id("bid")\
                    .find_element_by_class_name("choice")\
                    .find_elements_by_class_name("popular")

                while len(game_elements) > 0:
                    highlighted_game = game_elements[-1]
                    if highlighted_game.text in not_allowed_games:
                        del(game_elements[-1])
                    else:
                        self.click_execute(highlighted_game)
                        self.tool.set_game(highlighted_game.text)
                        break

                self.time_util(3, "Čakamo na izbiro drugih igralcov")
                self.check_state(state_name)
                if self.state == "call":
                    if self.driver.find_element_by_id("call").find_element_by_css_selector("h2").text.startswith(self.player_name):
                        self.my_bot_playing = True
                        self.tool.set_bot_game()
                        Logs.info_message(choose_game_message + "I'm playing game -> " + str(self.tool.game))
                    choose_over = True

                if choose_over or not self.check_state(state_name):
                    break

        except NoSuchElementException:
            Logs.error_message("No game was found in " + choose_game_message)
            raise NoSuchElementException

    def choose_king(self):
        choose_king_message = "Connector.choose_king(): "
        Logs.debug_message(choose_king_message + "Choosing King")
        state_name = "call"

        if not self.check_state(state_name):
            Logs.info_message(choose_king_message + "Ending because not in right state")
            return

        try:
            if self.driver.find_element_by_id("call").find_element_by_css_selector("h2").text.startswith(self.player_name):
                self.my_bot_playing = True
                self.tool.set_bot_game()
                Logs.info_message(choose_king_message + "I'm playing game -> " + str(self.tool.game))
        except NoSuchElementException:
            Logs.error_message("Error in: " + choose_king_message)
            raise NoSuchElementException

        if self.my_bot_playing:
            self.time_util(1, "Izbiramo kralja")
            suite = self.tool.choose_king()
            try:
                self.click_execute(
                    self.driver.find_element_by_id("call").find_element_by_css_selector("img[alt='" + suite + "']")
                )
            except NoSuchElementException:
                Logs.error_message("Error in: " + choose_king_message)
                raise NoSuchElementException
        else:
            self.time_util(1, "Čakamo da drug igralec izbere kralja")

    def choose_talon(self):
        choose_talon_message = "Connector.choose_talon(): "
        Logs.debug_message(choose_talon_message + "Choosing talon")
        state_name = "talon"

        if not self.check_state(state_name):
            Logs.info_message(choose_talon_message + "Ending because not in right state")
            return

        talon_online_cards = []

        if self.my_bot_playing:
            try:
                # Step 1 - izbira talona
                talon_cards = self.driver.find_element_by_id("talon").find_element_by_class_name("data")\
                    .find_elements_by_css_selector("img")
                Logs.debug_message(choose_talon_message + "po vrsti karte iz talona")
                self.talon_located = True
                for talon_card in talon_cards:
                    Logs.debug_message(talon_card.get_attribute("alt"))
                    talon_online_cards.append(talon_card.get_attribute("alt"))
                talon_index = self.tool.choose_talon_step_1(talon_online_cards)
                self.click_execute(talon_cards[talon_index])

                # Step 2 - Zalaganje
                self.time_util(1)
                self.get_cards()
                non_disabled_card_indexes = self.get_non_disabled_card_indexes()
                Logs.debug_message("$$$$$$$$$$ Non disabled card indexes $$$$$$$$$$$$")
                Logs.debug_message(non_disabled_card_indexes)
                disposed_cards_index = self.tool.choose_talon_step_2(non_disabled_card_indexes)
                Logs.debug_message("$$$$$$$$$$ disposed_cards_index $$$$$$$$$$$$")
                Logs.debug_message(disposed_cards_index)
                Logs.debug_message("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                for card_index in disposed_cards_index:
                    Logs.info_message(choose_talon_message + "Card put down -> " +
                                      self.online_cards[card_index].get_attribute("alt"))
                    self.click_execute(self.online_cards[card_index])
                    self.time_util(1, "Waiting for another card to put down...")
            except NoSuchElementException:
                Logs.error_message("Error in: " + choose_talon_message)
                raise NoSuchElementException
        else:
            self.time_util(1, "Izbira talona od drugega igralca")
            if self.element_located("#talon .data img"):
                talon = self.driver.find_element_by_id("talon").find_element_by_class_name("data") \
                    .find_elements_by_css_selector("img")
                Logs.warning_message("Talon located from another player!!!! SUCCESS")
                self.talon_located = True
                for talon_card in talon:
                    Logs.debug_message(talon_card.get_attribute("alt"))
                    talon_online_cards.append(talon_card.get_attribute("alt"))

    def napoved(self):
        napoved_message = "Connector.napoved(): "
        Logs.debug_message(napoved_message + ": Napoved naprej")
        state_name = "bonus"

        if not self.check_state(state_name):
            Logs.info_message(napoved_message + ": Ending because not in right state")
            return

        if not self.tool.is_my_turn(self.get_timers(1)):
            return

        try:
            self.click_execute(
                self.driver.find_element_by_id("bonus").find_element_by_css_selector("input[name='announce']")
            )
        except NoSuchElementException:
            Logs.error_message("Error in: " + napoved_message)
            raise NoSuchElementException

    def the_game(self):
        message = "Connector.the_game()"
        Logs.debug_message(message + ": Starting game")
        state_name = "game"

        if not self.check_state(state_name):
            Logs.info_message(message + ": Ending because not in right state")
            return

        # stack0 - me, stack1 - right, stack2 - up, stack3 - left
        player_positions = {"stack0": "", "stack1": "", "stack2": "", "stack3": ""}
        position_names = config["player_positions"].split(",")

        try:
            rounds_left = 12 if self.is_four_players else 16
            while True:
                if self.check_if_reset():
                    return
                if len(self.tool.cards) < 2 or rounds_left < 2:
                    break
                # TODO preverji če se je okno za naslednjo rundo pojavu
                if self.tool.is_my_turn(self.get_timers(2)):
                    self.check_for_ally()
                    table, card_counter = self.get_cards_from_table(player_positions)
                    Logs.debug_message("############ TABLE ############")
                    Logs.debug_message(table)
                    Logs.debug_message("###############################")
                    self.get_cards()
                    indexes = self.get_non_disabled_card_indexes()
                    play = self.tool.play_card(indexes, table)
                    try:
                        table["stack0"] = self.online_cards[play].get_attribute("alt")
                    except StaleElementReferenceException:
                        Logs.error_message(message + "selenium.common.exceptions.StaleElementReferenceException: Possible card missing?! skipping round")
                        continue
                    self.click_execute(self.online_cards[play])
                    rounds_left -= 1
                    Logs.info_message("Rounds Left: " + str(rounds_left))

                    for position in position_names:
                        if table[position] == "" and card_counter > 0 and self.element_located("#" + position + " img"):
                            table[position] = self.driver.find_element_by_id(position)\
                                .find_elements_by_css_selector("img")[0]\
                                .get_attribute("alt")
                            card_counter -= 1

                    Logs.debug_message("####### WHOLE TABLE ############")
                    Logs.debug_message(table)
                    Logs.debug_message("################################")
                    # Odštejemo števce za karte in preverimo za možnega ally-ja
                    self.tool.set_suit_helper_objects_and_tarots(table)
                    # self.tool.check_for_ally(table)

                    # Reset the map
                    for p in player_positions:
                        player_positions[p] = ""

            while True:
                self.time_util(5, "waiting to get the last cards")
                self.get_cards()
                if len(self.tool.cards) == 0:
                    # Get last cards from table, valat.si automaticaly plays the last card for you so just get from table
                    for position in player_positions:
                        if player_positions[position] == "" and self.element_located("#" + position + " img"):
                            player_positions[position] = self.driver.find_element_by_id(position) \
                                .find_elements_by_css_selector("img")[0] \
                                .get_attribute("alt")

                    Logs.debug_message("####### LAST CARDS FOR WHOLE TABLE ############")
                    Logs.debug_message(player_positions)
                    Logs.debug_message("###############################################")
                    break

            self.state = "end_game"
            self.commit_to_database()

        except NoSuchElementException:
            Logs.error_message("Error in: " + message)
            raise NoSuchElementException

    def get_non_disabled_card_indexes(self):
        indexes = []
        for i in range(0, len(self.online_cards)):
            self.driver.implicitly_wait(1)
            Logs.debug_message(self.online_cards[i].get_attribute("alt"))
            Logs.debug_message(self.online_cards[i].get_attribute("class"))
            if "disabled" not in self.online_cards[i].get_attribute("class"):
                indexes.append(i)

        return indexes

    def get_cards_from_table(self, player_positions):
        message = "Connector.get_cards_from_table(): "
        positions = config["player_positions"].split(",")
        card_counter = 0
        for position in positions:
            elements = self.driver.find_element_by_id(position).find_elements_by_css_selector("img")
            if len(elements) > 0:
                alt = elements[0].get_attribute("alt")
                player_positions[position] = int(alt) if alt.isdigit() else alt
            else:
                card_counter += 1
                Logs.debug_message(message + "player: (" + position + ") has no card. Players to check later: " + str(card_counter))
        return player_positions, card_counter

    def get_timers(self, between_time=5):
        get_timers_message = "Connector.get_timers()"
        Logs.debug_message(get_timers_message + ": Start")

        start = self.driver.find_element_by_id("right"). \
            find_element_by_id("timer"). \
            find_element_by_class_name("time").text

        Logs.debug_message("Start timer obtained (" + start + "), waiting for end")
        for i in range(0, between_time):
            time.sleep(1)

        end = self.driver.find_element_by_id("right"). \
            find_element_by_id("timer"). \
            find_element_by_class_name("time").text
        Logs.info_message(get_timers_message + "'Start time: " + start + "', 'End time: " + end + "'")
        Logs.debug_message(get_timers_message + ": End")
        return [start, end]

    def element_located(self, selector):
        message = "Connector.element_located(): "
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            Logs.debug_message(message + "Element '" + selector + "' successfully located")
            return True
        except TimeoutException:
            Logs.warning_message(message + "Element '" + selector + "' not located!!!")
            return False

    def time_util(self, seconds, location=""):
        for i in range(0, seconds):
            Logs.debug_message("Connector.time_util(" + location + "): " + str(seconds - i))
            time.sleep(1)

    def check_state(self, state_name):
        try:
            bid_state = self.driver.find_element_by_id("bid").get_attribute("class") == "show"
            call_state = self.driver.find_element_by_id("call").get_attribute("class") == "show"
            talon_state = self.driver.find_element_by_id("talon").get_attribute("class") == "show"
            bonus_state = self.driver.find_element_by_id("bonus").get_attribute("class") == "show"
        except NoSuchElementException:
            Logs.error_message("ERROR in check_state()")
            raise NoSuchElementException

        Logs.debug_message("states:\nbid_state = " + bid_state.__str__() + "\ncall_state = " + call_state.__str__() +
                           "\ntalon_state = " + talon_state.__str__() + "\nbonus_state = " + bonus_state.__str__())
        if bid_state:
            self.state = "bid"
        elif call_state:
            self.state = "call"
        elif talon_state:
            self.state = "talon"
        elif bonus_state:
            self.state = "bonus"
        else:
            self.state = "game"

        if state_name != self.state:
            Logs.info_message("WRONG STATE. Current state: " + state_name + ", Last known state: " + self.state)
            return False
        return True

    def check_if_reset(self):
        message = "Connector.check_if_set_or_reset(): "
        if self.admin.bot_state == "reset":
            Logs.info_message(message + "Bot will now wait for your command")
            while True:
                time.sleep(1)
                if self.admin.bot_state == "set":
                    self.state = "end_game"
                    return True
        return False

    def commit_to_database(self):
        Db.connect_to_db()
        results = self.get_points_from_scores()
        Logs.debug_message(self.card_ids)
        self.tool.set_rounds_db(results,
                                2 if self.my_bot_playing else 1 if self.rufan else 0,
                                self.talon_located)
        Db.execute_sql(
            "INSERT INTO Rounds(bot_name, playing, points, tarot_count, color_points, game, played_suit, game_points, game_diff, bonuses, talon_located, time_stamp) " +
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            self.tool.rounds_db.get_values())
        last_id = Db.get_last_row_id()
        Logs.debug_message(last_id)
        Admin.last_row_id_from_db = last_id
        self.tool.set_roundCards_db(Db.get_last_row_id(), self.card_ids)
        Db.execute_sql("INSERT INTO RoundCards(round_id, card_id) VALUES (%s, %s)",
                       self.tool.roundCards_db.get_values(),
                       True)
        Db.close_db()

    def get_points_from_scores(self):
        message = "Connector.get_points_from_scores(): "
        game_points = 0
        game_diff = 0
        bonuses = 0
        try:
            data = self.driver.find_elements_by_css_selector("#scores .data table tr")
            Logs.debug_message(message + "Length of data is: " + str(len(data)))
            for i, row in enumerate(data):
                td_elements = row.find_elements_by_css_selector("td")
                for j, td in enumerate(td_elements):
                    if td.text != "" or td.text is not None:
                        val = td.text[1:]
                        Logs.debug_message(message + "current 'td.text'")
                        Logs.debug_message(td.text)
                        if val.isdigit():
                            if i == 0:
                                game_points = self.tool.extract_scores(td.text)
                            if i == 1:
                                game_diff = self.tool.extract_scores(td.text)
                            else:
                                bonuses += self.tool.extract_scores(td.text)

        except NoSuchElementException:
            Logs.error_message("Error in: " + message)
            Logs.warning_message("NoSuchElementException: Could not extract points from Scores!")
        except TypeError:
            Logs.error_message("Error in: " + message)
            Logs.warning_message("TypeError: Could not extract points from Scores!")

        result = {"game_points": game_points, "game_diff": game_diff, "bonuses": bonuses}
        Logs.debug_message(message + "Returning values from scores")
        Logs.debug_message(result)
        return result

    def check_for_ally(self):
        message = "Connector.check_for_ally(): "
        player_names = config["player_names"].split(",")
        player_map = {}
        if self.tool.is_ally_set():
            return
        if self.tool.game != 1 and self.tool.game != 2:
            Logs.debug_message(message + "No need to search for ally. Not known game")
            return
        for player_name in player_names:
            try:
                spans = self.driver.find_element_by_id(player_name).find_elements_by_css_selector(".bid span")
                if len(spans) > 0:
                    player_map[player_name] = spans
            except NoSuchElementException:
                Logs.error_message("Error in: " + message)
                Logs.warning_message("NoSuchElementException: Could not find ally")

        Logs.debug_message(message + "player map")
        Logs.debug_message(player_map)
        if len(player_map) == 1:
            # preverim če moj bot igra al pa če sem rufan
            possible_ally = list(player_map.keys())[0]
            if self.my_bot_playing:
                self.tool.set_ally(possible_ally)
                return

            alts = [online_card.get_attribute("alt") for online_card in self.online_cards]
            Logs.debug_message(message + "Printing alts")
            Logs.debug_message(alts)

            span_list = list(player_map.values())[0]

            player_properties = [s.text for s in span_list]
            Logs.debug_message(message + "Printing player_properties")
            Logs.debug_message(player_properties)

            """
            <div class="bid">
                <span title="Dve v križu">2</span>
                <span title="" class="emoji">♣</span>
            </div>
            """
            if player_properties[1] + "8" in alts:
                Logs.debug_message(message + "Found ally! Rufan")
                if player_properties[0].isdigit():
                    self.tool.game = int(player_properties[0])
                    self.tool.set_bot_game()
                self.rufan = True
                self.tool.set_ally(possible_ally)
                return

        if len(player_map) == 2:
            for pm in player_map:
                if pm in player_names:
                    player_names.remove(pm)

            if len(player_names) == 1:
                self.tool.set_ally(player_names[0])

    def close_connection(self):
        self.driver.close()
