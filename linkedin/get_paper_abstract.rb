# require 'linkedin-scraper'
require 'watir'
ERROR_MSG = "None"

def search(browser, keyword)
    """ Search for <keyword>, scrape the abstract of the first search result that has one """
    browser.text_field(id: "gs_hp_tsi").set(keyword)
    # click search button
    browser.button(id: "gs_hp_tsb").click
    # Read first abstract
    browser.div(class: "gs_rs").text
end

def afterSearchCleanup(browser)
    browser.goto("http://scholar.google.com")
end

def printAbstract(keyword)
    browser = Watir::Browser.new(:firefox)
    browser.goto("http://scholar.google.com")
    begin
        puts(search(browser, keyword))
    rescue
        puts(ERROR_MSG)
        afterSearchCleanup(browser)
    end
    browser.close
end

if ARGV.length != 1
    puts("usage: ruby get_paper_abstract.rb keyword")
    exit
end

keyword = ARGV[0]
Watir.default_timeout = 10
printAbstract(keyword)
