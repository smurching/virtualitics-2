# require 'linkedin-scraper'
require 'watir'
require_relative 'Linkedin'

# def getProfileFromUrl(url)
#     Linkedin::Profile.new(url, { company_details: true })
# end

# def getProfile(username)
#     getProfileFromURL("http://www.linkedin.com/in/#{username}")    
# end

# def toJson(profile)
#     res = {}
#     res["first_name"] = profile.first_name          # The first name of the contact
#     res["last_name"] = profile.last_name           # The last name of the contact
#     res["name"] = profile.name                # The full name of the profile
#     res["title"] = profile.title               # The job title
#     res["summary"] = profile.summary             # The summary of the profile
#     res["location"] = profile.location            # The location of the contact
#     res["country"] = profile.country             # The country of the contact
#     res["industry"] = profile.industry            # The domain for which the contact belongs
#     res["picture"] = profile.picture             # The profile picture link of profile
#     res["skills"] = profile.skills              # Array of skills of the profile
#     res["organizations"] = profile.organizations       # Array organizations of the profile
#     res["education"] = profile.education           # Array of hashes for education
#     res["websites"] = profile.websites            # Array of websites
#     res["groups"] = profile.groups              # Array of groups
#     res["languages"] = profile.languages           # Array of languages
#     res["certifications"] = profile.certifications      # Array of certifications
#     res["number_of_connections"] = profile.number_of_connections # The number of connections as a string
#     res.to_json
# end

def login(browser, username, password)
    browser.goto "http://linkedin.com"
    browser.text_field(id: 'login-email').set(username)
    browser.text_field(id: 'login-password').set(password)   
    browser.button(id: 'login-submit').click
end

def search(browser, keyword)
    """ Search for <keyword>, go to the page of the user corresponding to the first search result and scrape it """
    browser.text_field(placeholder: 'Search').set("#{keyword} chemistry body armor")
    # Try clicking two different kinds of search button
    doSearchButton = browser.button(class: "nav-search-button")
    if doSearchButton.exists?
        doSearchButton.click
    else
        browser.button(class: "submit-button").click
    end    
    # Go to page corresponding to first search result, get profile info
    firstSearchResult = browser.span(class: "name-and-icon")
    if firstSearchResult.text.include?("LinkedIn Member")
        raise "First search result was an out of network LinkedIn Member"
    else
        browser.span(class: "name-and-icon").click
    end
    # Wait for page to load
    Watir::Wait.until { 
      profileUrlString = "linkedin.com/in/"
      puts("Waiting for url to include #{profileUrlString}..., current url: #{browser.url}")        
      browser.url.include?(profileUrlString)
    }
    attributes = getAttributes(browser)

end

def getTextFromClass(browser, tag, className, isPlural=false)
  elem = browser.send(tag, {class: className})
  if isPlural
    elem.map do |htmlElem| htmlElem.text end
  elsif elem.exists?
    elem.text.strip 
  else
    nil
  end
end

def getSummary(browser)
  # Click see more button if one exists
  seeMoreButton = browser.button(class: "truncate-multiline--button")
  if seeMoreButton.exists?
    seeMoreButton.click
  end
  # Get summary text, slice off garbage text at end
  rawSummary = getTextFromClass(browser, "p", "pv-top-card-section__summary")
  if rawSummary.nil?
    return nil
  end

  endIndex = rawSummary.index("See less") || rawSummary.index("See more")
  if !rawSummary.nil? and !endIndex.nil?
    rawSummary.slice(0..(endIndex - 1)).tr("\n", " ")
  else
    nil
  end
end

def getAttributes(browser)
    """ Scrape attributes from current page, assumed to be a single user's linkedin profile. """
    res = {}
    res["name"] = getTextFromClass(browser, "h1", "pv-top-card-section__name")
    res["title"] = getTextFromClass(browser, "h2", "pv-top-card-section__headline")
    # res["company"] = getTextFromClass(browser, "h3", "pv-top-card-section__company")
    res["companies"] = getTextFromClass(browser, "spans", "pv-position-entity__secondary-title", true)
    res["school"] = getTextFromClass(browser, "h3", "pv-top-card-section__school")
    res["summary"] = getSummary(browser) 
    res.to_json
end

def processName(rawName)
    names = rawName.split(" ")
    # Remove middle name(s)
    if names.length > 1
        names.first + " " + names.last
    else
        names.first
    end
end

def loadAuthorList(filename)
    authorNames = []
    File.open(filename, "r") do |f|
      f.each_line do |line|
        authorNames <<= processName(line.split(",")[0])
      end
    end    
    authorNames
end

def afterSearchCleanup(browser)
    # button = browser.button(data-is-animating-click "true")
    # TODO: Conditional error handling/cleanup for failed searches
    browser.goto("http://linkedin.com")
end

def getProfiles(username, password, authorsFilename, outputFilename)
    browser = Watir::Browser.new(:firefox)
    login(browser, username, password)
    names = loadAuthorList(authorsFilename)
    File.open(outputFilename, "w") do |f|
        for name in names
            begin
                f.write("#{search(browser, name)}\n")
            rescue
                puts("Error occurred while searching for name #{name}, continuing...")
                afterSearchCleanup(browser)                 
            end           
        end
    end
end

if ARGV.length != 3
    puts("usage: ruby linkedin_scrape.rb authors_filename linkedin_username linkedin_password")
    exit
end

authorsFilename = ARGV[0]
username = ARGV[1]
password = ARGV[2]
Watir.default_timeout = 5
getProfiles(username, password, authorsFilename, "#{authorsFilename}.processed")
