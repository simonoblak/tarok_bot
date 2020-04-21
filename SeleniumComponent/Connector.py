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
from ProjectConstants.PlayingStatus import PlayingStatus
from ProjectConstants.CardRanks import CardRanks
from ProjectConstants.AdminState import AdminState
from ProjectConstants.ConnectorState import ConnectorState
from CrashWarn.MusicPlayer import MusicPlayer
from CrashWarn.EmailSender import send_email
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
        self.wait = WebDriverWait(self.driver, 10)
        self.is_four_players = config["player_number"] == 4
        self.player_name = ""
        self.player_names = ()
        self.tool = bot_logic.Tools.Tools()
        self.my_bot_playing = False
        self.choose_king_done = False
        self.choose_talon_done = False
        self.rufan = False
        self.is_game_selected_naprej = False
        self.talon_located = False
        self.talon_subtracted = False
        self.state = ConnectorState.BID
        self.online_cards = []
        self.online_alts = []
        self.card_ids = []
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

    def init_round(self):
        self.my_bot_playing = False
        self.tool.init_round()
        self.card_ids = self.tool.get_card_ids()
        self.talon_subtracted = False
        self.rufan = False
        self.is_game_selected_naprej = False
        self.choose_king_done = False
        self.choose_talon_done = False
        self.talon_located = False
        if Logs.counter_for_errors > 0:
            Logs.warning_message("There were " + str(Logs.counter_for_errors) + " errors in previous round")
            Logs.reset_error_counter()

    def click_execute(self, element):
        Logs.debug_message("Connector.click_execute: " + element.text)
        self.driver.execute_script("arguments[0].click();", element)

    def add_bots(self, bot, number_of_players):
        for i in range(1, number_of_players):
            self.click_execute(bot)

    def login(self):
        user_config = [line.rstrip('\n') for line in open(config["user_config"])]

        # Set username by email of the player
        # self.player_name = user_config[0].split("@")[0].lower()

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
        message = "Connector.create_game()"
        Logs.info_message("Creating game: " + message)

        try:
            # Saving nickname
            self.player_name = self.driver.find_element_by_css_selector("#profile h3").text.lower()
            self.player_names = (self.player_name, "horjul123", "lucka zagar", "develop simon")

            # Create new game
            self.time_util(config["time_to_wait"], "pred klikom za novo igro")
            self.driver.implicitly_wait(3)
            create_new_game = self.driver.find_element_by_id("new")
            self.click_execute(create_new_game)

            if not self.is_four_players:
                set_for_three_players = self.driver \
                    .find_element_by_css_selector("div[class='seats']") \
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

            # self.time_util(5)
            create_game = self.driver.find_element_by_css_selector("input[name='create']")
            self.click_execute(create_game)

            bot_difficulty = self.driver.find_element_by_class_name("ai").find_elements_by_css_selector("span")
            for bot in bot_difficulty:
                if opponent_bot == bot.text:
                    self.add_bots(bot, config["player_number"])
                    break
            return

        except NoSuchElementException:
            Logs.warning_message(message + "Could not start new game, trying to enter existing game")

        Logs.warning_message("Stopping the bot")
        self.admin.set_bot_state(AdminState.RESET)
        # self.time_util(10)

    def get_cards(self):
        get_cards_message = "Connector.get_cards(): "
        Logs.debug_message(get_cards_message + "Getting cards...")

        self.online_alts = []
        try:
            self.online_cards = self.driver.find_element_by_id("cards").find_elements_by_css_selector("img")
            for online_card in self.online_cards:
                alt = online_card.get_attribute("alt")
                self.online_alts.append(alt)
                Logs.debug_message(get_cards_message + "Added -> " + alt)
            self.tool.convert_online_cards_into_bot_format(self.online_alts)
        except NoSuchElementException:
            Logs.error_message("No element found in: " + get_cards_message)
            # raise NoSuchElementException
        except StaleElementReferenceException:
            Logs.error_message("Stale element reference: element is not attached to the page document")

    def choose_game(self):
        message = "Connector.choose_game(): "
        Logs.debug_message(message + "Choosing game")
        state_name = ConnectorState.BID
        is_over_counter = 0
        self.init_round()
        if self.check_if_reset():
            return

        while True:
            my_turn = self.tool.is_my_turn(self.get_timers(1))
            Logs.debug_message(message + "tool.is_my_turn -> " + str(my_turn))
            if my_turn:
                break
            else:
                self.time_util(1, message)
                is_over_counter += 1
                if is_over_counter > 20:
                    self.state = ConnectorState.OVER
                    return

        choose_over = False
        try:
            not_allowed_games = config["not_allowed_games"].split(",")

            while True:
                game_elements = self.driver.find_element_by_id(ConnectorState.BID) \
                    .find_element_by_class_name("choice") \
                    .find_elements_by_class_name("popular")

                while len(game_elements) > 0:
                    highlighted_game = game_elements[-1]
                    highlighted_text = highlighted_game.text
                    if highlighted_text in not_allowed_games:
                        del(game_elements[-1])
                    else:
                        self.click_execute(highlighted_game)
                        self.tool.set_game(highlighted_text)
                        if highlighted_text is not None and highlighted_text.lower() == "naprej":
                            self.is_game_selected_naprej = True
                            Logs.info_message(message + "is_game_selected_naprej = True")
                        break

                self.time_util(3, "Čakamo na izbiro drugih igralcov")
                self.check_state(state_name)
                if self.state == ConnectorState.CALL:
                    if self.is_game_selected_naprej:
                        Logs.debug_message(message + "NAPREJ!!")
                        break
                    if self.driver.find_element_by_id(ConnectorState.CALL).find_element_by_css_selector("h2").text.lower().startswith(self.player_names):
                        self.my_bot_playing = True
                        self.tool.set_playing_status(PlayingStatus.PLAYING)
                        self.tool.set_bot_game()
                        Logs.info_message(message + "I'm playing game -> " + str(self.tool.game))
                    choose_over = True

                if choose_over or not self.check_state(state_name):
                    break

        except NoSuchElementException:
            Logs.error_message("No game was found in " + message)
            # raise NoSuchElementException
            Logs.warning_message("Stopping the bot")
            self.admin.set_bot_state(AdminState.RESET)

    def choose_king(self):
        choose_king_message = "Connector.choose_king(): "
        Logs.debug_message(choose_king_message + "Choosing King")
        state_name = ConnectorState.CALL
        if self.check_if_reset():
            return

        if not self.check_state(state_name):
            Logs.info_message(choose_king_message + "Ending because not in right state")
            return

        if not self.is_game_selected_naprej:
            try:
                if self.driver.find_element_by_id(ConnectorState.CALL).find_element_by_css_selector("h2").text.lower().startswith(self.player_names):
                    self.my_bot_playing = True
                    self.tool.set_bot_game()
                    Logs.info_message(choose_king_message + "I'm playing game -> " + str(self.tool.game))
            except NoSuchElementException:
                Logs.error_message("Error in: " + choose_king_message)
                # raise NoSuchElementException
                Logs.warning_message("Stopping the bot")
                self.admin.set_bot_state(AdminState.RESET)

        if self.my_bot_playing and not self.choose_king_done:
            self.time_util(1, "Izbiramo kralja")
            suite = self.tool.choose_king()
            try:
                self.click_execute(
                    self.driver.find_element_by_id(ConnectorState.CALL).find_element_by_css_selector("img[alt='" + suite + "']")
                )
                self.choose_king_done = True
            except NoSuchElementException:
                Logs.error_message("Error in: " + choose_king_message)
                # raise NoSuchElementException
                Logs.warning_message("Stopping the bot")
                self.admin.set_bot_state(AdminState.RESET)
        else:
            self.time_util(1, "Čakamo da drug igralec izbere kralja")

    def choose_talon(self):
        message = "Connector.choose_talon(): "
        Logs.debug_message(message + "Choosing talon")
        state_name = ConnectorState.TALON
        if self.check_if_reset():
            return

        if not self.check_state(state_name):
            Logs.info_message(message + "Ending because not in right state")
            return

        talon_online_cards = []

        if self.my_bot_playing and not self.choose_talon_done:
            try:
                # Step 1 - izbira talona
                talon_cards = self.driver.find_element_by_id(ConnectorState.TALON).find_element_by_class_name("data")\
                    .find_elements_by_css_selector("img")
                Logs.debug_message(message + "po vrsti karte iz talona")
                self.talon_located = True
                for talon_card in talon_cards:
                    Logs.debug_message(talon_card.get_attribute("alt"))
                    talon_online_cards.append(talon_card.get_attribute("alt"))
                talon_index = self.tool.choose_talon_step_1(talon_online_cards)
                self.click_execute(talon_cards[talon_index])

                # Step 2 - Zalaganje
                self.time_util(1)
                self.get_cards()
                self.tool.count_tarots_in_hand_and_color_points()
                non_disabled_card_indexes = self.get_non_disabled_card_indexes()
                disposed_card_alts = self.tool.choose_talon_step_2(non_disabled_card_indexes)
                for card_alt in disposed_card_alts:
                    Logs.info_message(message + "Card put down -> " + str(card_alt))

                    self.click_execute(
                        self.driver.find_element_by_id("cards").find_element_by_css_selector("img[alt='" + card_alt + "']")
                    )
                    self.time_util(1, "Waiting for another card to put down...")
                self.choose_talon_done = True
            except NoSuchElementException:
                Logs.error_message("Error in: " + message)
                # raise NoSuchElementException
                Logs.warning_message("Stopping the bot")
                self.admin.set_bot_state(AdminState.RESET)
        else:
            self.time_util(1, "Izbira talona od drugega igralca")
            self.tool.count_tarots_in_hand_and_color_points()
            if self.element_located("#talon .data img"):
                talon = self.driver.find_element_by_id(ConnectorState.TALON).find_element_by_class_name("data") \
                    .find_elements_by_css_selector("img")
                Logs.info_message("Talon located from another player!!!! SUCCESS")
                self.talon_located = True
                selected_talon_alts = []
                try:
                    for talon_card in talon:
                        alt = talon_card.get_attribute("alt")
                        Logs.debug_message(alt)
                        if "disabled" in talon_card.get_attribute("class"):
                            Logs.debug_message(message + "Card '" + alt + "' was added to talon_online_cards")
                            talon_online_cards.append(alt)
                        else:
                            selected_talon_alts.append(alt)
                except StaleElementReferenceException:
                    Logs.error_message("Stale element reference: element is not attached to the page document")
                if len(talon_online_cards) > 0 and not self.talon_subtracted:
                    Logs.info_message(message + "Talon will be subtracted")
                    self.tool.set_suit_helper_objects_and_tarots_and_history(None, talon_online_cards)
                    self.tool.selected_talon_alts = selected_talon_alts
                    self.talon_subtracted = True

    def napoved(self):
        napoved_message = "Connector.napoved(): "
        Logs.debug_message(napoved_message + ": Napoved naprej")
        state_name = ConnectorState.BONUS
        if self.check_if_reset():
            return

        if not self.check_state(state_name):
            Logs.info_message(napoved_message + ": Ending because not in right state")
            return

        if not self.tool.is_my_turn(self.get_timers(1)):
            return

        self.get_cards()
        self.tool.count_colors_kings_and_trula()

        try:
            self.click_execute(
                self.driver.find_element_by_id(ConnectorState.BONUS).find_element_by_css_selector("input[name='announce']")
            )
        except NoSuchElementException:
            Logs.error_message("Error in: " + napoved_message)
            # raise NoSuchElementException
            Logs.warning_message("Stopping the bot")
            self.admin.set_bot_state(AdminState.RESET)

    def the_game(self):
        message = "Connector.the_game(): "
        Logs.debug_message(message + ": Starting game")
        state_name = ConnectorState.GAME

        if not self.check_state(state_name):
            Logs.info_message(message + ": Ending because not in right state")
            return

        # stack0 - me, stack1 - right, stack2 - up, stack3 - left
        player_positions = {"stack0": "", "stack1": "", "stack2": "", "stack3": ""}
        position_names = config["player_positions"].split(",")

        try:
            rounds_left = 12 if self.is_four_players else 16
            reset_counter = 0
            previous_table = []
            while True:
                if self.check_if_reset():
                    return
                if len(self.tool.cards) < 2 or rounds_left < 2:
                    break
                if self.tool.is_my_turn(self.get_timers(2)):
                    self.check_for_ally()
                    table, card_counter = self.get_cards_from_table(player_positions)
                    Logs.debug_message("############ TABLE ############")
                    Logs.debug_message(table)
                    Logs.debug_message("###############################")
                    """
                    # Checking if lag or something caused that cards didn't disappear
                    is_previous_table_same = False
                    for stack in table:
                        if table[stack] in previous_table:
                            is_previous_table_same = True
                            Logs.info_message(message + "Previous table is same. Breaking because of lag.")
                            for p in player_positions:
                                player_positions[p] = ""
                            break
                    if is_previous_table_same:
                        continue
                    """
                    self.get_cards()
                    indexes = self.get_non_disabled_card_indexes()
                    play = self.tool.play_card(indexes, table)
                    table["stack0"] = play
                    # try:
                    #     pass
                    #     # table["stack0"] = self.online_cards[play].get_attribute("alt")
                    # except StaleElementReferenceException:
                    #     Logs.error_message(message + "selenium.common.exceptions.StaleElementReferenceException: Possible card missing?! skipping round")
                    #     continue

                    self.click_execute(
                        self.driver.find_element_by_id("cards").find_element_by_css_selector("img[alt='" + play + "']")
                    )
                    rounds_left -= 1
                    Logs.info_message("Rounds Left: " + str(rounds_left))

                    for position in position_names:
                        if table[position] == "" and card_counter > 0 and self.element_located("#" + position + " img"):
                            alt = self.driver.find_element_by_id(position) \
                                .find_elements_by_css_selector("img")[0] \
                                .get_attribute("alt")
                            table[position] = int(alt) if alt.isdigit() else alt
                            card_counter -= 1

                    previous_table = list(table.values())
                    Logs.debug_message("####### WHOLE TABLE ############")
                    Logs.debug_message(table)
                    Logs.debug_message("################################")
                    # Odštejemo števce za karte in preverimo za možnega ally-ja
                    self.tool.set_suit_helper_objects_and_tarots_and_history(table)
                    # self.tool.check_for_ally(table)

                    # Reset the map
                    for p in player_positions:
                        player_positions[p] = ""
                else:
                    reset_counter += 1
                    if reset_counter > 10:
                        Logs.info_message(message + "exiting because it's probably over")
                        self.state = ConnectorState.END_GAME
                        return
                if self.tool.not_supported_game:
                    scores_state = False
                    try:
                        scores_state = self.driver.find_element_by_id(ConnectorState.BID).get_attribute("class") == "show"
                    except NoSuchElementException:
                        Logs.error_message("ERROR while checking state")
                        # raise NoSuchElementException
                    if scores_state:
                        self.state = ConnectorState.END_GAME
                        MusicPlayer.stop_sound()
                        return

            waiting_counter = 0
            while True:
                self.time_util(5, "waiting to get the last cards")
                if waiting_counter > 4:
                    Logs.error_message(message + "This is taking to long, something is wrong")
                    raise Exception
                waiting_counter += 1
                self.get_cards()
                if len(self.tool.cards) == 0:
                    # Get last cards from table, valat.si automaticaly plays the last card for you so just get from table
                    for position in player_positions:
                        if player_positions[position] == "" and self.element_located("#" + position + " img"):
                            alt = self.driver.find_element_by_id(position) \
                                .find_elements_by_css_selector("img")[0] \
                                .get_attribute("alt")
                            player_positions[position] = int(alt) if alt.isdigit() else alt

                        if not self.tool.is_ally_set() and not isinstance(player_positions[position], int):
                            if player_positions[position] == self.tool.get_playing_suit() + CardRanks.KING:
                                Logs.info_message(message + "Found ally in last round.")
                                stacks = config["player_positions"].split(",")
                                for s in [position] + [self.tool.playing_player]:
                                    if s in stacks:
                                        stacks.remove(s)
                                    else:
                                        Logs.info_message(message + "Cannot remove stack from final round check for ally!")
                                self.tool.set_ally(stacks[0])

                    Logs.debug_message("####### LAST CARDS FOR WHOLE TABLE ############")
                    Logs.debug_message(player_positions)
                    Logs.debug_message("###############################################")
                    self.tool.set_suit_helper_objects_and_tarots_and_history(player_positions, None)
                    break

            self.state = ConnectorState.END_GAME
            self.commit_to_database()

        except NoSuchElementException:
            Logs.error_message("Error in: " + message)
            Logs.warning_message("Stopping the bot")
            self.admin.set_bot_state(AdminState.RESET)
            # raise NoSuchElementException

    def get_non_disabled_card_indexes(self):
        indexes = []
        for i in range(0, len(self.online_cards)):
            self.driver.implicitly_wait(1)
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
        bid_state = False
        call_state = False
        talon_state = False
        bonus_state = False
        try:
            bid_state = self.driver.find_element_by_id(ConnectorState.BID).get_attribute("class") == "show"
            call_state = self.driver.find_element_by_id(ConnectorState.CALL).get_attribute("class") == "show"
            talon_state = self.driver.find_element_by_id(ConnectorState.TALON).get_attribute("class") == "show"
            bonus_state = self.driver.find_element_by_id(ConnectorState.BONUS).get_attribute("class") == "show"
        except NoSuchElementException:
            Logs.error_message("ERROR in check_state()")
            # raise NoSuchElementException

        Logs.debug_message("states:\nbid_state = " + bid_state.__str__() + "\ncall_state = " + call_state.__str__() +
                           "\ntalon_state = " + talon_state.__str__() + "\nbonus_state = " + bonus_state.__str__())
        if bid_state:
            self.state = ConnectorState.BID
        elif call_state:
            self.state = ConnectorState.CALL
        elif talon_state:
            self.state = ConnectorState.TALON
        elif bonus_state:
            self.state = ConnectorState.BONUS
        else:
            self.state = ConnectorState.GAME

        if state_name != self.state:
            Logs.info_message("WRONG STATE. Current state: " + state_name + ", Last known state: " + self.state)
            return False
        return True

    def check_if_reset(self):
        message = "Connector.check_if_set_or_reset(): "
        if self.admin.bot_state == AdminState.RESET:
            Logs.info_message(message + "Bot will now wait for your command")
            while True:
                time.sleep(1)
                if self.admin.bot_state == AdminState.SET:
                    self.state = ConnectorState.END_GAME
                    return True
        return False

    def commit_to_database(self):
        Db.connect_to_db()
        results = self.get_points_from_scores()
        Logs.debug_message(self.card_ids)

        self.tool.set_rounds_db(results, self.talon_located)
        Db.execute_sql(
            "INSERT INTO Rounds(bot_name, playing, points, tarot_count, color_points, game, played_suit, game_points, " +
            "game_diff, bonuses, ally, king_count, trula_count, talon_points, num_of_colors, talon_located, time_stamp)" +
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            self.tool.rounds_db.get_values())

        last_id = Db.get_last_row_id()
        Logs.debug_message(last_id)
        self.admin.last_row_id_from_db = last_id
        for stack in ["talon", "stack0"] + config["player_positions"].split(","):
            self.tool.set_roundCards_db(last_id, self.card_ids, stack)
            Db.execute_sql("INSERT INTO RoundCards(round_id, card_id, is_from_talon, put_down, player) VALUES (%s, %s, %s, %s, %s)",
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
                for td in td_elements:
                    if td.text != "" or td.text is not None:
                        val = td.text[1:]
                        Logs.debug_message(message + "current 'td.text'")
                        Logs.debug_message(td.text)
                        if val.isdigit():
                            if i == 0:
                                game_points = self.tool.extract_scores(td.text)
                            if i == 1:
                                game_diff = self.tool.extract_scores(td.text)
                            if i >= 2:
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
        if self.tool.is_ally_set() or self.tool.playing_status == PlayingStatus.ALONE or self.tool.not_supported_game:
            return
        for player_name in player_names:
            try:
                spans = self.driver.find_element_by_id(player_name).find_elements_by_css_selector(".bid span")
                if len(spans) > 0:
                    player_map[player_name] = spans
                    # red_class = self.driver.find_element_by_id(player_name).find_elements_by_css_selector(".bid span[class='red']")
                    #
                    # Logs.debug_message(message + "red_class = spans[0].find_elements_by_css_selector(#" + player_name + " .bid span[class='red'])")
                    # Logs.debug_message(red_class)
                    # if red_class is not None and len(red_class) > 0:
                    #     self.tool.playing_status = PlayingStatus.ALONE

            except NoSuchElementException:
                Logs.error_message("Error in: " + message)
                Logs.warning_message("NoSuchElementException: Could not find ally")

        Logs.debug_message(message + "player map")
        Logs.debug_message(player_map.keys())
        if len(player_map) == 1:
            # preverim če moj bot igra al pa če sem rufan
            possible_ally = list(player_map.keys())[0]
            if self.my_bot_playing and possible_ally != "":
                self.tool.set_ally("stack" + possible_ally[-1])
                return

            Logs.debug_message(message + "Printing alts")
            Logs.debug_message(self.online_alts)

            span_list = list(player_map.values())[0]

            player_properties = [s.text for s in span_list]
            Logs.debug_message(message + "Printing player_properties")
            Logs.debug_message(player_properties)

            if len(player_properties) == 2 and self.tool.playing_player == "":
                if player_properties[0].isdigit():
                    self.tool.game = int(player_properties[0])
                    self.tool.set_bot_game()
                self.tool.set_playing_suit(player_properties[1])
                self.tool.playing_player = "stack" + possible_ally[-1]

            """
            <div class="bid">
                <span title="Dve v križu">2</span>
                <span title="" class="emoji">♣</span>
            </div>
            """
            if player_properties[0].isdigit() and player_properties[1] + CardRanks.KING in self.online_alts:
                Logs.debug_message(message + "Found ally! Rufan")
                self.rufan = True
                self.tool.set_playing_status(PlayingStatus.RUFAN)
                self.tool.set_ally("stack" + possible_ally[-1])
                return

            # Looking for un supported games: Berač, Solo, Klop
            if player_properties[0] in ('B', 'S', 'K'):
                Logs.info_message(message + "Game is not supported. Will turn on random card selector.")
                self.tool.not_supported_game = True
                MusicPlayer.play_sound(config["not_supported_game"])
                send_email("Unsupported game is in play!")
                return

        if len(player_map) == 2:
            Logs.debug_message(message + "Found two players in ally check")
            is_game_number_found = False
            playing_game = 0
            playing_suit = ""
            for pm in player_map:
                player_properties = [s.text for s in player_map[pm]]
                Logs.debug_message(message + "Printing player_properties")
                Logs.debug_message(player_properties)

                for pp in player_properties:
                    if pp.isdigit():
                        is_game_number_found = True
                        playing_game = int(pp)
                    elif pp in config["suit_signs"].split(","):
                        playing_suit = pp
                        self.tool.playing_player = "stack" + pm[-1]

                if pm in player_names:
                    player_names.remove(pm)

            if is_game_number_found:
                self.tool.game = playing_game
                self.tool.set_bot_game()
                self.tool.set_playing_suit(playing_suit)
            if len(player_names) == 1:
                self.tool.set_ally("stack" + player_names[0][-1])

    def close_connection(self):
        self.driver.close()
