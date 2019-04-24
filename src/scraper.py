import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import random
import pandas as pd



def get_products_on_page(driver):
    items = []
    table_id = driver.find_element_by_class_name("ProductsPage__right___3ywMl")
    rows = table_id.find_elements_by_xpath(".//div[contains(@id, 'item-')]")
    for row in rows:
        itemID = row.get_attribute("id")
        print(itemID)
        itemNum = itemID.split("-")[1]
        items.append(itemNum)
        anchor = row.find_element_by_css_selector("div a")
        href = anchor.get_attribute("href")
        print(href)

    # click dat bell pepper
    rows[0].find_element_by_css_selector("div a").click()
    print(items[0], "\n" in items[0])
    time.sleep(10)

pageURL = "https://grocery.walmart.com/browse/Fresh-Vegetables?aisle=1255027787131_1255027789453"

driver = webdriver.Firefox()
driver.get(pageURL)

time.sleep(30)
get_products_on_page(driver)
driver.quit()
