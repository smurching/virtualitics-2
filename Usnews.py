import requests
from BeautifulSoup import BeautifulSoup
import re
import csv

csv_file = open('USNews_rankings.csv', 'wb', buffering=0)
writer = csv.writer(csv_file)


urls = ['https://www.usnews.com/education/best-global-universities/rankings?page='+str(i) for i in range(2, 100)]
urls = ['https://www.usnews.com/education/best-global-universities/rankings'] + urls
print urls
records = []
ranks = []
names = []
locations = []
for url in urls:
    r = requests.get(url, headers = {"User-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"})
    soup = BeautifulSoup(r.text)
    for rank in soup.findAll('span', attrs={'class': 'rankscore-bronze'}):
        ranks.append(int(re.findall('\d+', rank.text)[0]))
    for college in soup.findAll('h2', attrs={'class': 'h-taut'}):
        names.append(college.text)
    for location in soup.findAll('span', attrs={'class': 't-dim t-small'}):
        locations.append(location.text)
    print ranks, names, locations

print len(ranks), len(names), len(locations)
# print ranks
for i in range(len(ranks)):
    records.append(ranks[i])
    records.append(names[i].encode('utf-8'))
    records.append(locations[i].encode('utf-8'))
    writer.writerow(records)
    records = []
