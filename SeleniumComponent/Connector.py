import time
import bot_logic.Tools
import Configuration
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

config = Configuration.Configuration().get_config()


"""
NOTES
https://selenium-python.readthedocs.io/installation.html


https://stackoverflow.com/questions/45347675/make-selenium-wait-10-seconds

set_page_load_timeout - Sets the amount of time to wait for a page load to complete before throwing an error. If the timeout is negative, page loads can be indefinite.

implicitly_wait - Specifies the amount of time the driver should wait when searching for an element if it is not immediately present.

set_script_timeout - Sets the amount of time to wait for an asynchronous script to finish execution before throwing an error. If the timeout is negative, then the script will be allowed to run indefinitely.
"""


class Connector:
    def __init__(self, url):
        self.url = url
        self.driver = self.init_driver()
        self.is_four_players = config["player_number"] == 4
        self.player_name = ""
        self.tool = bot_logic.Tools.Tools()
        self.my_bot_playing = False
        self.state = "bid"
        self.online_cards = []

    def init_driver(self):
        init_driver_message = "Connector.init_driver()"
        print("Initialising driver for '" + self.url + "': " + init_driver_message)
        # Disabling notifications from web pages
        options_for_chrome = webdriver.ChromeOptions()
        options_for_chrome.add_argument("--disable-notifications")

        # Open chrome and set needed parameters
        web_driver = webdriver.Chrome(options=options_for_chrome)
        web_driver.maximize_window()
        web_driver.get(self.url)
        web_driver.implicitly_wait(5)
        print("Finished: " + init_driver_message)
        return web_driver

    def click_execute(self, element):
        print("Connector.click_execute: " + element.text)
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

        pw_input = self.driver.find_element_by_css_selector("input[name='password']")
        pw_input.send_keys(user_config[1] + Keys.ENTER)
        self.driver.implicitly_wait(5)

    def create_game(self, opponent_bot):
        create_game_message = "Connector.create_game()"
        print("Creating game: " + create_game_message)

        try:
            # Leave the try catch for the other parameters for setting the game

            # Create new game
            self.time_util(20, "pred klikom za novo igro")
            self.driver.implicitly_wait(3)
            create_new_game = self.driver.find_element_by_id("new")
            self.click_execute(create_new_game)

            if not self.is_four_players:
                set_for_three_players = self.driver\
                    .find_element_by_css_selector("div[class='seats']")\
                    .find_element_by_id("seats3")

                self.click_execute(set_for_three_players)

            # TODO set the other elements here
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

            #self.state = "Game created"

        except NoSuchElementException:
            print("No element found in: " + create_game_message)
            raise NoSuchElementException

    def get_cards(self):
        get_cards_message = "Connector.get_cards()"
        print(get_cards_message + ": Getting cards...")
        state_name = "Get Cards"

        alts = []
        try:
            self.online_cards = self.driver.find_element_by_id("cards").find_elements_by_css_selector("img")
            for online_card in self.online_cards:
                alt = online_card.get_attribute("alt")
                alts.append(alt)
                print(get_cards_message + ": Added -> " + alt)
        except NoSuchElementException:
            print("No element found in: " + get_cards_message)
            raise NoSuchElementException

        self.tool.convert_online_cards_into_bot_format(alts)

    def choose_game(self):
        choose_game_message = "Connector.choose_game()"
        print(choose_game_message + ": Choosing game")
        state_name = "bid"
        # self.check_state(state_name)

        while True:
            my_turn = self.tool.is_my_turn(self.get_timers(1))
            print(choose_game_message + ": tool.is_my_turn -> " + str(my_turn))
            if my_turn:
                break
            else:
                time.sleep(1)

        choose_over = False
        try:
            not_allowed_games = config["not_allowed_games"].split(",")

            while True:
                # self.driver.implicitly_wait(10)
                # self.time_util(5, "choose_game")
                game_elements = self.driver.find_element_by_id("bid")\
                    .find_element_by_class_name("choice")\
                    .find_elements_by_class_name("popular")

                while len(game_elements) > 0:
                    highlighted_game = game_elements[-1]
                    if highlighted_game.text in not_allowed_games:
                        del(game_elements[-1])
                    else:
                        self.click_execute(highlighted_game)
                        self.tool.game = highlighted_game.text
                        break

                # self.driver.implicitly_wait(5)
                self.time_util(3, "Čakamo na izbiro drugih igralcov")
                self.check_state(state_name)
                if self.state == "call":
                    if self.driver.find_element_by_id("call").find_element_by_css_selector("h2").text.startswith(self.player_name):
                        self.my_bot_playing = True
                    choose_over = True

                if choose_over or not self.check_state(state_name):
                    break

        except NoSuchElementException:
            print("No game was found in " + choose_game_message)
            raise NoSuchElementException

    def choose_king(self):
        choose_king_message = "Connector.choose_king()"
        print(choose_king_message + ": Choosing King")
        state_name = "call"

        if not self.check_state(state_name):
            print(choose_king_message + ": Ending because not in right state")
            return

        if self.my_bot_playing:
            self.time_util(1, "Izbiramo kralja")
            suite = self.tool.choose_king()
            try:
                if suite == 'Clubs':
                    self.click_execute(self.driver.find_element_by_id("call").find_element_by_css_selector("img[alt='♣8']"))
                elif suite == 'Hearts':
                    self.click_execute(self.driver.find_element_by_id("call").find_element_by_css_selector("img[alt='♥8']"))
                elif suite == 'Spades':
                    self.click_execute(self.driver.find_element_by_id("call").find_element_by_css_selector("img[alt='♠8']"))
                elif suite == 'Diamonds':
                    self.click_execute(self.driver.find_element_by_id("call").find_element_by_css_selector("img[alt='♦8']"))
            except NoSuchElementException:
                print("Error in: " + choose_king_message)
                raise NoSuchElementException
        else:
            self.time_util(1, "Čakamo da drug igralec izbere kralja")

    def choose_talon(self):
        choose_talon_message = "Connector.choose_talon()"
        print(choose_talon_message + ": Choosing talon")
        state_name = "talon"

        if not self.check_state(state_name):
            print(choose_talon_message + ": Ending because not in right state")
            return

        talon_online_cards = []

        if self.my_bot_playing:
            try:
                # Step 1 - izbira talona
                talon_cards = self.driver.find_element_by_id("talon").find_element_by_class_name("data")\
                    .find_elements_by_css_selector("img")
                print(choose_talon_message + ": po vrsti karte iz talona")
                for talon_card in talon_cards:
                    print(talon_card.get_attribute("alt"))
                    talon_online_cards.append(talon_card.get_attribute("alt"))
                talon_index = self.tool.choose_talon_step_1(talon_online_cards)
                self.click_execute(talon_cards[talon_index])

                # Step 2 - Zalaganje
                self.time_util(1)
                self.get_cards()
                non_disabled_card_indexes = self.get_non_disabled_card_indexes()
                print("$$$$$$$$$$ Non disabled card indexes $$$$$$$$$$$$")
                print(non_disabled_card_indexes)
                disposed_cards_index = self.tool.choose_talon_step_2(non_disabled_card_indexes)
                print("$$$$$$$$$$ disposed_cards_index $$$$$$$$$$$$")
                print(disposed_cards_index)
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                for card_index in disposed_cards_index:
                    print(choose_talon_message + ": Card put down -> " +
                          self.online_cards[card_index].get_attribute("alt"))
                    self.click_execute(self.online_cards[card_index])
                    self.time_util(1, "Waiting for another card to put down...")
            except NoSuchElementException:
                print("Error in: " + choose_talon_message)
                raise NoSuchElementException
        else:
            self.time_util(1, "Izbira talona od drugega igralca")

    def napoved(self):
        napoved_message = "Connector.napoved()"
        print(napoved_message + ": Napoved naprej")
        state_name = "bonus"

        if not self.check_state(state_name):
            print(napoved_message + ": Ending because not in right state")
            return

        if not self.tool.is_my_turn(self.get_timers(1)):
            return

        try:
            self.click_execute(self.driver.find_element_by_id("bonus")
                               .find_element_by_css_selector("input[name='announce']"))
        except NoSuchElementException:
            print("Error in: " + napoved_message)
            raise NoSuchElementException

    def the_game(self):
        the_game_message = "Connector.the_game()"
        print(the_game_message + ": Starting game")
        state_name = "game"

        if not self.check_state(state_name):
            print(the_game_message + ": Ending because not in right state")
            return
        # end = False
        # stack0 - me, stack1 - right, stack2 - up, stack3 - left
        player_positions = {"stack0": "", "stack1": "", "stack2": "", "stack3": ""}

        try:
            # self.is_tarot = True if "tarot" == suit else False    # value_when_true if condition else value_when_false
            rounds_left = 12 if self.is_four_players else 16
            while rounds_left > 0:
                if self.tool.is_my_turn(self.get_timers(2)):
                    table = self.get_cards_from_table(player_positions)
                    print("############ TABLE ############")
                    print(table)
                    print("###############################")
                    self.get_cards()
                    indexes = self.get_non_disabled_card_indexes()
                    play = self.tool.play_card(indexes, table)
                    self.click_execute(self.online_cards[play])
                    rounds_left -= 1
                    print("Rounds Left: " + str(rounds_left))

                    # TODO this might come in handy https://stackoverflow.com/a/51534196/11189926

                    # Reset the map
                    for p in player_positions:
                        player_positions[p] = ""

            # self.time_util(15, "Waiting for next game")
            self.state = "end_game"
        except NoSuchElementException:
            print("Error in: " + the_game_message)
            raise NoSuchElementException

    def get_non_disabled_card_indexes(self):
        indexes = []
        for i in range(0, len(self.online_cards)):
            self.driver.implicitly_wait(1)
            print(self.online_cards[i].get_attribute("alt"))
            print(self.online_cards[i].get_attribute("class"))
            if "disabled" not in self.online_cards[i].get_attribute("class"):
                indexes.append(i)

        """
        for i in range(0, len(self.online_cards)):
            while True:
                self.driver.implicitly_wait(1)
                if "disabled" not in self.online_cards[i].get_attribute("class"):
                    indexes.append(i)
                
                c = self.online_cards[i].get_attribute("class")
                if c is not None:
                    
                        break
                else:
                    print("Something wrong, there is no class in 'Connector.get_non_disabled_card_indexes()'")
                    self.time_util(1)
        """
        return indexes

    def get_cards_from_table(self, player_positions):
        message = "Connector.get_cards_from_table(): "
        for position in ["stack1", "stack2", "stack3"]:  # config["player_positions"].split(",")
            elements = self.driver.find_element_by_id(position).find_elements_by_css_selector("img")
            if len(elements) > 0:
                alt = elements[0].get_attribute("alt")
                player_positions[position] = int(alt) if alt.isdigit() else alt
            else:
                print(message + "player: (" + position + ") has no card")
        return player_positions

    def get_timers(self, between_time=5):
        get_timers_message = "Connector.get_timers()"
        print(get_timers_message + ": Start")

        start = self.driver.find_element_by_id("right"). \
            find_element_by_id("timer"). \
            find_element_by_class_name("time").text

        print("Start timer obtained (" + start + "), waiting for end")
        for i in range(0, between_time):
            time.sleep(1)

        end = self.driver.find_element_by_id("right"). \
            find_element_by_id("timer"). \
            find_element_by_class_name("time").text
        print(get_timers_message + "'Start time: " + start + "', 'End time: " + end + "'")
        print(get_timers_message + ": End")
        return [start, end]

    def time_util(self, seconds, location=""):
        for i in range(0, seconds):
            print("Connector.time_util(" + location + "): " + str(seconds - i))
            time.sleep(1)

    def check_state(self, state_name):
        try:
            bid_state = self.driver.find_element_by_id("bid").get_attribute("class") == "show"
            call_state = self.driver.find_element_by_id("call").get_attribute("class") == "show"
            talon_state = self.driver.find_element_by_id("talon").get_attribute("class") == "show"
            bonus_state = self.driver.find_element_by_id("bonus").get_attribute("class") == "show"
        except NoSuchElementException:
            print("ERROR in check_state()")
            raise NoSuchElementException

        print("states:\nbid_state = " + bid_state.__str__() + "\ncall_state = " + call_state.__str__() +
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
            print("WRONG STATE. Current state: " + state_name + ", Last known state: " + self.state)
            return False
        return True

    def close_connection(self):
        self.driver.close()
