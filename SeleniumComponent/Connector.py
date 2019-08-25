import time
import bot_logic.Tools
import Configuration
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

config = Configuration.Configuration().get_config()


"""
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

        except NoSuchElementException:
            print("No element found in: " + create_game_message)
            raise NoSuchElementException

    def get_cards(self):
        get_cards_message = "Connector.get_cards()"
        print(get_cards_message + ": Getting cards...")

        alts = []
        try:
            online_cards = self.driver.find_element_by_id("cards").find_elements_by_css_selector("img")
            for online_card in online_cards:
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

        timers = self.get_timers()
        while True:
            my_turn = self.tool.is_my_turn(timers)
            print(choose_game_message + ": tool.is_my_turn -> " + str(my_turn))
            if my_turn:
                break
            else:
                time.sleep(1)

        choose_over = False
        try:
            not_allowed_games = config["not_allowed_games"].split(",")

            while True:
                #self.driver.implicitly_wait(10)
                self.time_util(10, "choose_game")
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

                self.driver.implicitly_wait(5)
                self.time_util(5, "Čakamo na izbiro drugih igralcov")
                print(choose_game_message +
                      ": Kralji class -> " +
                      self.driver.find_element_by_id("call").get_attribute("class"))
                if self.driver.find_element_by_id("call").get_attribute("class") == "show":
                    if self.driver.find_element_by_id("call").find_element_by_css_selector("h2").text == self.player_name:
                        self.my_bot_playing = True
                    choose_over = True

                if choose_over:
                    break

        except NoSuchElementException:
            print("No game was found in " + choose_game_message)
            raise NoSuchElementException

    def choose_king(self):
        choose_king_message = "Connector.choose_king()"
        print(choose_king_message + ": Choosing King")
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

    def choose_talon(self):
        choose_talon_message = "Connector.choose_talon()"
        print(choose_talon_message + ": Choosing talon")
        talon_index = self.tool.choose_talon()
        #try:
        #    self.driver.find_element_by_id("talon").find_element_by_class_name("data")

    def get_timers(self, between_time=5):
        get_timers_message = "Connector.get_timers()"
        print(get_timers_message + ": Start")

        start = self.driver.find_element_by_id("right").\
            find_element_by_id("timer").\
            find_element_by_class_name("time").text

        for i in range(0, between_time):
            print("Start timer obtained (" + start + "), waiting for end")
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

    def close_connection(self):
        self.driver.close()


"""
elem = driver.find_element_by_id("email")
elem.send_keys(user)
elem = driver.find_element_by_id("pass")
elem.send_keys(pwd)
elem.send_keys(Keys.RETURN)
driver.implicitly_wait(5)
#elem = driver.find_element_by_id("u_g_2")
#elem = driver.find_elements_by_css_selector()
#elem.send_keys("Miha Trobec")

elems = driver.find_elements_by_css_selector("input[placeholder='Iskanje']")

elem = elems[1]
driver.implicitly_wait(5)
elem.send_keys(person)
chatsearch = driver.find_element_by_id("chatsearch")
chatlistbox = chatsearch.find_element_by_css_selector("ul[role='listbox']")
chatlistbox.click()

nek = driver.switch_to.active_element
nek.send_keys(text1)
'''
chattextboxes = driver.find_elements_by_class_name("fbNubFlyoutFooter")
chattextbox = chattextboxes[0].find_element_by_css_selector("br[data-text='true']")
chattextbox.send_keys("Lego my fego ego")

'''
#chatlistbox.send_keys("testisi")
driver.implicitly_wait(2)
print("zdele bom poslal!!!!!!!!!!!!!!!")
chatsend = driver.find_element_by_css_selector("a[label='send']")
chatsend.click()


driver.implicitly_wait(10)
#elem.send_keys(Keys.ENTER)
#driver.implicitly_wait(5)
#driver.close()






# https://selenium-python.readthedocs.io/installation.html
"""
