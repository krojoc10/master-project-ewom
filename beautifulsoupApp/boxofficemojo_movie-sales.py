from urllib import request
from bs4 import BeautifulSoup
import json
import datetime

#function to open page and create soup
def getSoup(url):
    webUrl = request.urlopen(url)
    pageContent = webUrl.read()
    return BeautifulSoup(pageContent, 'html.parser')

#function to extract page data
def extractPageData(data, soup):
    #save table rows as data records, delete header row
    dataRecords = soup.select('div#table div table tr')
    del dataRecords[0]

    #extract title and sales for every data record
    for dataRecord in dataRecords:
        salesData = {
            'movieName': dataRecord.find('td', class_='mojo-field-type-title').get_text(),
            'sales': dataRecord.find('td', class_='mojo-field-type-money').get_text()
        }
        print('item scraped: ', salesData)
        data.append(salesData)

    return data

#log start
startTime = datetime.datetime.now()
print('status: started')

#create empty data list
data = []

#create soup with inital url
soup = getSoup('https://www.boxofficemojo.com/chart/ww_top_lifetime_gross')

#loop for pagination
while True:
    #extract page data
    data = extractPageData(data, soup)
    
    #get pagination element
    nextPage = soup.select('div.mojo-pagination ul li.a-last')

    #go to next page if available
    if nextPage[0].find('a'):
        nextPage = 'https://www.boxofficemojo.com' + nextPage[0].find('a')['href']
        soup = getSoup(nextPage)
    #exit if next page is not available
    else:
        break

#log finish
finishTime = datetime.datetime.now()
print('status: finished')
elapsedTime = datetime.timedelta.total_seconds(finishTime - startTime)

#print stats
stats = {
    'start_time': startTime,
    'finish_time': finishTime,
    'elapsed_time_seconds': elapsedTime,
    'item_scraped_count': len(data)
    }

print(stats)

#convert data into json and write it to file
json_object = json.dumps(data)
with open("boxofficemojo-beautifulsoup-data.json", "w") as outfile:
    outfile.write(json_object)