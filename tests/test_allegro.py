import random
import string
import time

import pytest
import pytest_html
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


@pytest.fixture(params=['chrome', 'firefox'], scope='class')
def open_driver(request):
    """Spawns an instance of browser under the test"""
    if request.param == "chrome":
        web_driver = webdriver.Chrome()
    elif request.param == "firefox":
        web_driver = webdriver.Firefox()
    request.cls.driver = web_driver
    yield
    web_driver.close()


@pytest.mark.usefixtures("open_driver")
class Test_Allegro:
    def test_open_homepage(self):
        url = "http://allegro.pl"
        self.driver.get(url)

    def _random_character(self) -> str:
        return random.choice(string.ascii_lowercase)

    def test_find_items(self):
        # Close privacy notice
        close_popup_xpath = '//button[@data-role="close-and-accept-consent"]'
        self.driver.find_element_by_xpath(close_popup_xpath).click()
        # Select search box
        search_box_xpath = '//input[@type="search"]'
        search = self.driver.find_element_by_xpath(search_box_xpath)
        # Search for a random items
        query = self._random_character()
        search.send_keys(query)
        search.submit()
        time.sleep(5)

    def test_filter_items(self):
        # Iterate over checkboxes
        checkboxes_xpath = '//label[@class="_u2xi2 _1xzdi _1wulo _1vzz9 _3e3a8_3Bcvi"]'
        checkboxes = self.driver.find_elements_by_xpath(checkboxes_xpath)
        # Filter for used items
        used_item_checkbox_xpath = './/*[contains(text(), "używane")]'
        for checkbox in checkboxes:
            try:
                checkbox.find_element_by_xpath(used_item_checkbox_xpath)
                checkbox.click()
                break
            except (NoSuchElementException, StaleElementReferenceException) as e:
                pass
        time.sleep(10)
        # Filter for items more expensive than 200 PLN
        price = "200,01"
        price_from_box_xpath = '//input[@type="text" and @id="price_from"]'
        price_from = self.driver.find_element_by_xpath(price_from_box_xpath)
        price_from.send_keys(price)
        # time.sleep(3)
        # price_from.submit()
        time.sleep(10)

    def _select_random_item(self):
        items = self.driver.find_elements_by_xpath('//article[@data-role="offer"]')
        return random.choice(items)

    def test_open_item(self):
        item = self._select_random_item()
        item.click()
        time.sleep(5)

    def test_add_to_shopping_cart(self):
        # Save item name
        item_name_xpath = "//meta[@itemprop='name']"
        global selected_item
        selected_item = self.driver.current_url
        # Add to cart
        add_to_cart_button_xpath = '//button[@id="add-to-cart-button"]'
        self.driver.find_element_by_xpath(add_to_cart_button_xpath).click()
        time.sleep(3)
        self.driver.find_element_by_xpath('//img[@alt="zamknij"]').click()
        time.sleep(5)

    def test_shopping_cart_content(self):
        # Open shopping cart
        shopping_cart_xpath = "//img[@alt='Koszyk']"
        self.driver.find_element_by_xpath(shopping_cart_xpath).click()
        time.sleep(5)
        # Find name of item in cart
        item_xpath = '//a[contains(@href, "https://allegro.pl/oferta/")]'
        item_in_cart = self.driver.find_element_by_xpath(item_xpath).get_attribute("href")
        # Make sure titles match
        assert selected_item == item_in_cart
