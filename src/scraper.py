import urllib.request
import urllib.robotparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import scrapy
import time
import random
import logging
import pandas as pd

logger = logging.getLogger("crawler_application")
logger.setLevel(logging.DEBUG)


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
    storeId = "1320"
    navButtons = {
            "Fruits&VegetablesBtn": ["HealthySnackingLink", "OrganicProduceLink", "FreshFruitLink", "FreshVegetablesLink",
                "FreshPreparedProduceLink", "FreshHerbsLink", "VegetarianProteins&AsianLink", "Nuts,DriedFruit,&HealthySnacksLink"], 

            "MeatBtn": ["BeefLink", "ChickenLink", "TurkeyLink", "Bacon,HotDogs&SausageLink", "SeafoodLink",
                "Specialty&OrganicMeatLink"],

            "Eggs&DairyBtn": ["CheeseLink"]
            }


    def __init__(self, robotsURL):
        super().__init__(robotsURL)
   

    def rand_sleep(self):
        return round(random.uniform(10,14), 2)

    
    def _build_api_link(self, product_link):
        if self.storeID == "" or self.storeID == None:
            print("Failed to build API link, store ID not set") #TODO: logging
            return ""

        productID = product_link.split("/")[-1]
        logger.debug("Product ID: {}".format(productID))
        return "https://grocery.walmart.com/v3/api/products/" + productID +
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
                    print(link)
                    links.append(link)
                except:
                    print("That fucked up")

        return links


    def fetch_products(self, baseURL="https://grocery.walmart.com"):
        driver = webdriver.Firefox()
        driver.get(baseURL)
        time.sleep(11) # Give Selenium time to load everything

        dept_links = self._get_department_links(driver)
        product_links = []
        product_api_links = []
        for link in dept_links:
            driver.get(link)
            try:
                product_anchors = driver.find_elements_by_css_selector("a[data-automation-id='link']")
                for a in product_anchors: 
                    href = a.get_attribute("href")
                    api = self._build_api_link(href)
                    product_api_links.append(api)
                    product_links.append(href)
            except:
                print("That fucked up")
            time.sleep(self.rand_sleep())
        print(product_links)

            

        """
        departmentElements = driver.find_elements_by_class_name("NavigationPanel__aisle___24DGq")
        for department in departmentElements:
        #for department in random.shuffle(departmentElements):
            hover = ActionChains(driver).move_to_element(department)
            hover.perform()
            time.sleep(self.rand_sleep())
            department.click()
  
            try:
                btn = driver.find_element_by_css_selector("a[data-automation-id='HealthySnackingLink']")
                link = btn.get_attribute("href")
                print(link)
            except:
                print("That fucked up")

        """ 
#            departmentShelf= driver.find_elements_by_class_name("NavigationPanel__item___2JSjO NavigationPanel__flex___2-fWp")
#            for shelf in departmentShelf: 



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
wc = WalmartCrawler("http://www.walmart.com/robots.txt")
wc.fetch_products()
#wc.fetch_products("https://grocery.walmart.com")
