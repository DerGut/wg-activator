#!/usr/bin/env python3
import logging
import random
import time
from configparser import ConfigParser

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

logging.basicConfig(
    filename='updates.log',
    filemode='a',
    level=logging.INFO,
    format='%(levelname)s::%(asctime)-15s::%(message)s'
)

# Load configuration
config = ConfigParser()
conf_file = open('config.ini')
config.readfp(conf_file)
USERNAME = config.get('Login', 'email')
PASSWORD = config.get('Login', 'password')
LISTING_URL = config.get('Listing', 'listing_url')
DELAY = int(config.get('Driver', 'delay'))
ENV = config.get('System', 'environment')
MARGIN = config.get('Driver', 'margin')

logging.info('Starting up...')

# Login
options = Options()
if ENV == 'production':
    options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
driver.get('https://wg-gesucht.de')

# Remove cookie button
btn = driver.find_element_by_id("cookie-confirm").click()
driver.find_element_by_link_text("LOGIN").click()
time.sleep(1)
username = driver.find_element_by_name("login_email_username")
password = driver.find_element_by_id("login_password")
username.send_keys(USERNAME)
password.send_keys(PASSWORD)
driver.find_element_by_id('login_submit').click()
time.sleep(5)

while True:
    try:
        # Open listing
        driver.get(
            LISTING_URL)
        time.sleep(3)
        contact = driver.find_element_by_class_name('bottom_contact_box')
        edit = contact.find_element_by_link_text('ANGEBOT BEARBEITEN')
        edit.send_keys(Keys.TAB)
        time.sleep(1)
        edit.click()
        time.sleep(3)

        # Refresh listing
        btn = driver.find_element_by_class_name('btn-orange') # weiter
        btn.send_keys(Keys.TAB)
        time.sleep(2)
        btn.send_keys(Keys.SPACE)
        btn = driver.find_element_by_class_name('btn-orange') # Änderungen ubernehmen
        btn.send_keys(Keys.TAB)
        time.sleep(2)
        btn.send_keys(Keys.SPACE)

        assert 'zehn Minuten' in driver.page_source

        logging.info("Reloaded")

    except NoSuchElementException as e:
        logging.error(f"{e}\nTry to increase the waiting time if the page wasn't fully loaded")
    except WebDriverException as e:
        logging.error(e)

    # offset = percent of margin around delay
    if MARGIN and MARGIN.isdigit() and MARGIN != 0.0:
        offset = DELAY * ((random.random() * MARGIN * 2) - MARGIN)
    else:
        offset = 0.0

    logging.info(f"Sleeping for {(DELAY + offset) // 60}min")

    time.sleep(DELAY + offset)
