// Import the module in your file 
var ScrapeLinkedin = require("scrape-linkedin");
 
// Create the scraper object 
var scrapper = new ScrapeLinkedin();
 
// Fetch a profile 
scrapper.fetch("charlyberthet")
// Handle the result 
.then(profile => console.log(profile))
// Handle an error 
.catch(err => console.log(err));