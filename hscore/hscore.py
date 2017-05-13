from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

API_URL = "https://www.scopus.com/freelookup/form/author.uri"

def getDriver():
    # Instantiate an instance of Remote WebDriver with the desired capabilities.
    return webdriver.PhantomJS()

def getById(driver, id):
    return driver.find_element_by_id(id)

def getByClass(driver, className):
    return driver.find_element_by_class_name(className)

def sendText(elem, text):
    elem.send_keys(text)

def root(driver):
    # Load search page 
    driver.get(API_URL)

def getIndex(driver, firstName, lastName):
    """
    Main method: pass in driver object corresponding to a browser window 
    (obtained from getDriver()), and the target researcher's first/last name. Returns the 
    researcher's hscore as an int.
    """
    root(driver)
    # Enter first/last name
    sendText(getById(driver, "firstname"), firstName)    
    sendText(getById(driver, "lastname"), lastName)
    # Uncheck exact search box
    getById(driver, "exactSearchCheck").click()    
    # Click search button
    getByClass(driver, "authorSearch").click()
    time.sleep(1)
    # Locate first search result
    # driver.find_element_by_xpath("//div[@class='dataCol2']//div//a").click()
    driver.find_element_by_class_name("dataCol2").find_element_by_tag_name("div").find_element_by_tag_name("a").click()
    time.sleep(1)
    return int(driver.find_element_by_class_name("row3").find_element_by_class_name("valueColumn").find_elements_by_tag_name("span")[0].text)

if __name__ == "__main__":
    driver = getDriver()
    print(getIndex(driver, "Geoffrey", "Hinton"))
    driver.close()


