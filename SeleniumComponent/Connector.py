from selenium import webdriver
from selenium.webdriver.common.keys import Keys

text1 = "Pozdravljeni"
url = "https://valat.si/tarok"

options_for_chrome = webdriver.ChromeOptions()
options_for_chrome.add_argument("--disable-notifications")

driver = webdriver.Chrome(options=options_for_chrome)
driver.maximize_window()
driver.get(url)
#assert "Valat" in driver.title
driver.implicitly_wait(5)
#google_registration = driver.find_element_by_class_name("go")
google_registration = driver.find_element_by_css_selector("a[class='go']")
driver.execute_script("arguments[0].click();", google_registration)
#google_registration.click()

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
