import logging
import random
import time
from configparser import ConfigParser

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(asctime)-15s:%(message)s'
)


def login():
    driver = webdriver.Remote("selenium-hub:4444/wd/hub", DesiredCapabilities.FIREFOX)
    driver.get('https://wg-gesucht.de')

    # Remove cookie button
    driver.find_element_by_id("cookie-confirm").click()
    driver.find_element_by_link_text("LOGIN").click()
    time.sleep(1)
    username = driver.find_element_by_name("login_email_username")
    password = driver.find_element_by_id("login_password")
    username.send_keys(USERNAME)
    password.send_keys(PASSWORD)
    driver.find_element_by_id('login_submit').click()
    time.sleep(5)

    return driver


def reload(driver):
    # Open listing
    driver.get(EDIT_URL)
    time.sleep(3)

    # Refresh listing
    def orange_button():
        return driver.find_element_by_class_name('btn-orange')

    # weiter
    orange_button().send_keys(Keys.TAB)
    time.sleep(2)
    orange_button().send_keys(Keys.SPACE)

    # Änderungen ubernehmen
    orange_button().send_keys(Keys.TAB)
    time.sleep(2)
    orange_button().send_keys(Keys.SPACE)


if __name__ == '__main__':
    # Load configuration
    config = ConfigParser()
    conf_file = open('config.ini')
    config.readfp(conf_file)

    USERNAME = config.get('Login', 'email')
    PASSWORD = config.get('Login', 'password')
    LISTING_ID = config.get('Listing', 'listing_id')
    LISTING_URL = "https://www.wg-gesucht.de/{}.html".format(LISTING_ID)
    EDIT_URL = "https://www.wg-gesucht.de/angebot-bearbeiten.html?edit={}".format(LISTING_ID)
    DELAY = int(config.get('Driver', 'delay'))
    ENV = config.get('System', 'environment')
    MARGIN = float(config.get('Driver', 'margin')) or 0.0

    logging.info('Starting up...')
    web_driver = login()

    while True:
        try:
            logging.info('Starting to reload')
            reload(web_driver)
            logging.info("Reloaded")
        except NoSuchElementException as e:
            logging.error(f"{e}\nTry to increase the waiting time if the page wasn't fully loaded")
        except WebDriverException as e:
            logging.error(e)
            web_driver.quit()
            web_driver = login()

        # offset = percent of margin around delay
        if MARGIN != 0.0:
            offset = int(DELAY * ((random.random() * MARGIN * 2.0) - MARGIN))
        else:
            offset = 0.0

        logging.info(f"Sleeping for {(DELAY + offset) // 60}min")
        time.sleep(DELAY + offset)
