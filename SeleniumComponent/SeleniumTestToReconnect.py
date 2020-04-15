from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class SeleniumTestToReconnect:
    def __init__(self):
        self.driver = self.init_driver()
        self.url = "https://valat.si/tarok"

    def init_driver(self):
        # Disabling notifications from web pages
        options_for_chrome = webdriver.ChromeOptions()
        options_for_chrome.add_argument("--disable-notifications")

        # Open chrome and set needed parameters
        web_driver = webdriver.Chrome(options=options_for_chrome)
        web_driver.maximize_window()
        web_driver.get(self.url)
        web_driver.implicitly_wait(5)
        print("Finished initializing driver")
        return web_driver

    def reinit_driver(self):
        uuu = self.driver.command_executor._url
        ppp = self.driver.session_id

        self.driver = webdriver.Remote(command_executor=uuu, desired_capabilities={})
        self.driver.close()
        self.driver.session_id = ppp
        self.driver.get(self.url)
        print("Successfully reinitialized driver!!!!!")


