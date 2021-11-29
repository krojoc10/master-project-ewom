from urllib import request
from bs4 import BeautifulSoup
import json

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
            'title': dataRecord.find('td', class_='mojo-field-type-title').get_text(),
            'sales': dataRecord.find('td', class_='mojo-field-type-money').get_text()
        }
        data.append(salesData)

    return data

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

#convert data into json and write it to file
json_object = json.dumps(data)
with open("test.json", "w") as outfile:
    outfile.write(json_object)