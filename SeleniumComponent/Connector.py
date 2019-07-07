import Configuration
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

lines = [line.rstrip('\n') for line in open("../resources/user_config.txt")]
config = Configuration.Configuration().get_config()

text1 = "Pozdravljeni"
url = "https://valat.si/tarok" # config["url"]


def click_execute(element):
    driver.execute_script("arguments[0].click();", element)


def add_bots(bot):
    for i in range(0, 3):
        click_execute(bot)


# Disabling notifications from web pages
options_for_chrome = webdriver.ChromeOptions()
options_for_chrome.add_argument("--disable-notifications")

# Open chrome and set needed parameters
driver = webdriver.Chrome(options=options_for_chrome)
driver.maximize_window()
driver.get(url)
driver.implicitly_wait(5)

# Find the google account login
google_registration = driver.find_element_by_css_selector("a[class='go']")
click_execute(google_registration)

# Login to google account
username_input = driver.find_element_by_id("identifierId")
username_input.send_keys(lines[0] + Keys.ENTER)
driver.implicitly_wait(5)

pw_input = driver.find_element_by_css_selector("input[name='password']")
pw_input.send_keys(lines[1] + Keys.ENTER)
driver.implicitly_wait(5)

# Create new game
create_new_game = driver.find_element_by_id("new")
click_execute(create_new_game)

create_game = driver.find_element_by_css_selector("input[name='create']")
click_execute(create_game)

tezek_bot, vrazji_bot = driver.find_element_by_class_name("ai").find_elements_by_css_selector("span")
add_bots(vrazji_bot)


#driver.close()

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
