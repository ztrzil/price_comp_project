import urllib.request
import urllib.robotparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import scrapy
import time
import json
import random
from datetime import datetime, timedelta
import logging
import os
import pandas as pd

DATA_PATH = "data/"

logger = logging.getLogger("crawler_application")
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler('crawler.log')
fh.setLevel(logging.DEBUG)
# create console handler which logs debug messages
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("[%(asctime)s] - %(name)s - %(levelname)s - %(message)s", 
        datefmt="%d/%m/%Y %H:%M:%S")

fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

class Crawler(object):
    useragent = "*"

    def __init__(self, robotsURL):
        self.robotTxtObj = self.get_robots_txt_file(robotsURL)

        # set default rate of 1 request every 10s if none given by robots.txt
        self.rate = self.robotTxtObj.request_rate(self.useragent)
        if self.rate == None: self.rate = (1, 10)


    def get_robots_txt_file(self, url):
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(url)
        rp.read()

        return rp
    


class WalmartCrawler(Crawler):
    # Do I need useragent here?? Or just access it through parent?
    maxUpdateDelay = 3
    prodIDs = []
    productData = {}
    navButtons = {
            "Fruits&VegetablesBtn": ["HealthySnackingLink", "OrganicProduceLink", "FreshFruitLink", "FreshVegetablesLink",
                "FreshPreparedProduceLink", "FreshHerbsLink", "VegetarianProteins&AsianLink", "Nuts,DriedFruit,&HealthySnacksLink"], 

            "MeatBtn": ["BeefLink", "ChickenLink", "TurkeyLink", "Bacon,HotDogs&SausageLink", "SeafoodLink",
                "Specialty&OrganicMeatLink"],

            "Eggs&DairyBtn": ["CheeseLink"]
            }


    def __init__(self, robotsURL, storeID):
        super().__init__(robotsURL)
        self.storeID = str(storeID)
        if not self.__have_updated_products_for_store():
            self.__fetch_products()
            self.save_links()
        else: 
            print("Not updating products because they have been updated"
                    " within the given threshold. Lower threshold to update")
  

    def __have_updated_products_for_store(self):
        check = False 
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        rel_path = DATA_PATH 
        abs_file_path = os.path.join(script_dir, rel_path)
        files = os.listdir(abs_file_path)

        for f in files:
            if self.storeID in f:
                # if the file exists, check how old it is so we can determine if we should update
                fileTime = datetime.fromtimestamp(os.path.getctime(abs_file_path + "/" + f))
                ageToCheck = datetime.now() - timedelta(days=self.maxUpdateDelay) 
                logging.debug("Found the product ID file, checking its age")
                if fileTime >= ageToCheck:
                    logging.debug("File was created within the max age time frame, no need to update")
                    check = True
                break

        return check


        if not check: return check
        # if we have it, make sure it's up to date
        check = False

    def save_links(self):
        with open("data/productIDsStore" + self.storeID, "w") as fp:
            for prod in self.prodIDs:
                fp.write("%s\n" % prod)


    def rand_sleep(self):
        return round(random.uniform(10,14), 2)

    
    def _build_api_link(self, product_link):
        if self.storeID == "" or self.storeID == None:
            print("Failed to build API link, store ID not set") #TODO: logging
            return ""

        productID = product_link.split("/")[-1]

        logger.debug("Product ID: {}".format(productID))

        return "https://grocery.walmart.com/v3/api/products/" + productID + \
        "?itemFields=all&storeID=" + self.storeID




    def _get_department_links(self, driver):
        links = []

        # click on the drop down menu to reveal the departments
        navButton = driver.find_element_by_id("mobileNavigationBtn")
        navButton.click()

        for topLvlNavBtn, subNavBtns in self.navButtons.items():
            department = driver.find_element_by_css_selector("button[data-automation-id='{}']".format(topLvlNavBtn))
            hover = ActionChains(driver).move_to_element(department)
            hover.perform()
            time.sleep(self.rand_sleep())
            department.click()
            for elem in subNavBtns: 
                try:
                    btn = driver.find_element_by_css_selector("a[data-automation-id='{}']".format(elem))
                    link = btn.get_attribute("href")
                    logger.debug(link)
                    links.append(link)
                except:
                    print("That fucked up")

        return links


    def fetch_product_data(self, prodID):
        pass


    def __get_num_pages(self, driver):
        try:
            pagesObj = driver.find_element_by_css_selector("button[class='active']")
            ariaLabel = pagesObj.get_attribute("aria-label")
            logger.debug("ariaLabel: {}".format(ariaLabel))
            if "page" in ariaLabel.lower():
                numPages = int(ariaLabel.split(" ")[3])
        except: 
            logger.debug("Only a single page for this catagory")
            return 1

        return numPages



    def __fetch_products(self, baseURL="https://grocery.walmart.com"):
        driver = webdriver.Firefox()
        driver.get(baseURL)
        time.sleep(11) # Give Selenium time to load everything

        dept_links = self._get_department_links(driver)
        product_links = []
        product_api_links = []
        for link in dept_links:
            driver.get(link)
            numPages = self.__get_num_pages(driver)
            for page in range(1, numPages+1, 1):
                if page > 1: 
                    nextPageLink = link + "&page=" + str(page)
                    logger.debug("Getting products from page {}".format(page))
                    driver.get(nextPageLink)
                    self.rand_sleep()
                try:
                    product_anchors = driver.find_elements_by_css_selector("a[data-automation-id='link']")
                    for a in product_anchors: 
                        href = a.get_attribute("href")
                        product_links.append(href) #TODO: remove this
                        productID = href.split("/")[-1]
                        self.prodIDs.append(productID)
                except:
                    print("That fucked up")
                logger.debug("Pulled {} product links so far".format(len(product_links)))
                time.sleep(self.rand_sleep())

        driver.quit()




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

"""
pageURL = "https://grocery.walmart.com/browse/Fresh-Vegetables?aisle=1255027787131_1255027789453"

driver = webdriver.Firefox()
driver.get(pageURL)

time.sleep(30)
get_products_on_page(driver)
driver.quit()
"""
wc = WalmartCrawler("http://www.walmart.com/robots.txt", "1320")
#wc.fetch_products()
"""
    def _gen_product_ids(self, prodLinks):
        for prodLink in prodLinks:
            productID = prodLink.split("/")[-1]
            self.prodIDs.append(productID)
"""
