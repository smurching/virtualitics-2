from newspaper import Article
import sys
import requests
import json
import time
from selenium import webdriver

class NytimesAPI:
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.baseEndpoint = "https://api.nytimes.com/svc/search/v2" 
    def getUrls(self, keyword):
        payload = {"q" : keyword, "api-key" : self.apiKey, "sort" : "newest"}
        res = requests.get("%s/articlesearch.json"%(self.baseEndpoint), params=payload)
        json_data = json.loads(res.text)
        return [searchResult["web_url"] 
            for searchResult in json_data["response"]["docs"] if "archive" not in searchResult["snippet"].lower()]

class GoogleNews:
    def __init__(self):
        self.baseEndpoint = "http://news.google.com"        
        self.driver = self.getDriver()
        self.root()

    def getDriver(self):
        # return webdriver.PhantomJS()
        return webdriver.Firefox()

    def getById(self, id):
        return self.driver.find_element_by_id(id)

    def getByClass(self, className, plural=False):
        if plural:
            return self.driver.find_elements_by_class_name(className)
        return self.driver.find_element_by_class_name(className)

    def sendText(self, elem, text):
        elem.send_keys(text)

    def root(self):
        # Load search page 
        self.driver.get(self.baseEndpoint)        
        time.sleep(3)

    def getUrls(self, keyword):
        self.sendText(self.getById("gbqfq"), keyword)
        self.getById("gbqfb").click()
        time.sleep(3)
        return [elem.text for elem in self.getByClass("_HId", plural=True)]


def getArticle(url):
    newspaper = Article(url)
    newspaper.download()
    time.sleep(5)
    newspaper.parse()
    return newspaper

def searchHelper(source, keyword):
    """ Search a single news source for a keyword. """
    # for now just pick top news article for the source
    urls = source.getUrls(keyword)
    print("got %s urls"%len(urls))
    if len(urls) == 0:
        return None
    for url in urls:
        try:
            newspaper = getArticle(url)
        except Exception:
            newspaper = None
            continue
    if newspaper is None:
        return None

    result = {}
    result["title"] = newspaper.title
    result["summary"] = newspaper.text
    return result

def search(sources, keyword):
    return list(filter(lambda result: result is not None,
        [searchHelper(source, keyword) for source in sources]))


if __name__ == "__main__":
    keyword = sys.argv[1]
    apiKey = sys.argv[2]
    # sources = [NytimesAPI(apiKey)]
    sources = [GoogleNews()]
    search(sources, keyword)
