    require 'watir'
    browser = Watir::Browser.new(:firefox)    
    username = "bodyarmorlinkedin@gmail.com"
    password = "openwerx"
    keyword = "satya nadella"
    browser = Watir::Browser.new(:firefox)    
    browser.goto "http://linkedin.com"
    browser.text_field(id: 'login-email').set(username)
    browser.text_field(id: 'login-password').set(password)   
    browser.button(id: 'login-submit').click
    browser.text_field(placeholder: 'Search').set(keyword)
    browser.button(class: "nav-search-button").click
    # Go to page corresponding to first search result, get profile info
    browser.span(class: "name-and-icon").click    
    # Wait for page to load
    Watir::Wait.until { 
      puts("Waiting..., url: #{browser.url}")        
      browser.url.include?("linkedin.com/in/")
    }
    className = "pv-top-card-section__name"
    puts(browser.text_field(class: className).text)
