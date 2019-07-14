import Configuration
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

config = Configuration.Configuration().get_config()


class Connector:
    def __init__(self, url):
        self.url = url
        self.driver = self.init_driver()
        self.is_four_players = config["player_number"] == 4

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
        try:
            # Leave the try catch for the other parameters for setting the game

            # Create new game
            create_new_game = self.driver.find_element_by_id("new")
            self.click_execute(create_new_game)

            if config["player_number"] == 3:
                set_for_3_players = self.driver\
                    .find_element_by_css_selector("div[class='seats']")\
                    .find_element_by_id("seats3")

                self.click_execute(set_for_3_players)

            # TODO set the other elements here

            create_game = self.driver.find_element_by_css_selector("input[name='create']")
            self.click_execute(create_game)

            bot_difficulty = self.driver.find_element_by_class_name("ai").find_elements_by_css_selector("span")
            for bot in bot_difficulty:
                if opponent_bot == bot.text:
                    self.add_bots(bot, config["player_number"])
                    break
        except NoSuchElementException:
            print("No element found in: " + create_game_message)

    def choose_game(self):
        self.driver.find_element_by_id("bid").find_element_by_class_name("choice")

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
