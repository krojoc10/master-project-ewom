from urllib import request
from bs4 import BeautifulSoup
import json
import re

#function to open page and create soup
def getSoup(url):
    req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    pageContent = request.urlopen(req).read()
    return BeautifulSoup(pageContent, 'html.parser')

#function to extract urls for movie detail pages
def extractMovieDetailsUrl(movieDetailsUrls, soup):

    #get all a tag elements with link to movie detail page
    movieDetailsUrlElements = soup.select('a.title')

    #extract urls from a tag elements
    for movieDetailsUrlElement in movieDetailsUrlElements:
        movieDetailsUrls.append('https://www.metacritic.com' + movieDetailsUrlElement['href'])

    return movieDetailsUrls

#function to extract movie details
def extractMovieDetails(soup):
    productName = soup.select('div.product_page_title')[0].find('h1').get_text()
    type = 'Movie'
    metascore = soup.select('div.ms_wrapper table tr td.summary_right a')[0].find('span').get_text()
    userscore = soup.select('div.user_score_summary table tr td.summary_right a')[0].find('span').get_text()
    producer = soup.select('span.distributor')[0].find('a').get_text()
    summary = soup.select('div.summary_deck span')[1].find('span').get_text()
    productUrlSegment = re.findall('movie\/(.+)', soup.find('meta', property='og:url')['content'])[0]

    #create dictionary with movie data
    movieData = {
        'productName': productName,
        'type': type,
        'metascore': metascore,
        'userscore': userscore,
        'producer': producer,
        'summary': summary,
        'productUrlSegment': productUrlSegment
    }

    return movieData

#empty list to save urls to movie details pages in
movieDetailsUrls = []

#create soup with inital url
soup = getSoup('https://www.metacritic.com/browse/movies/score/metascore/all')

#get urls to movie detail pages with loop for pagination
while True:
    #extract page data
    movieDetailsUrls = extractMovieDetailsUrl(movieDetailsUrls, soup)
    
    #get pagination element
    nextPage = soup.select('div.page_flipper span.next')

    #go to next page if available
    if nextPage[0].find('a'):
        nextPage = 'https://www.metacritic.com' + nextPage[0].find('a')['href']
        soup = getSoup(nextPage)
    #exit if next page is not available
    else:
        break

#create empty data list
data = []

#extract movie details
for movieDetailsUrl in movieDetailsUrls:
    data.append(extractMovieDetails(getSoup(movieDetailsUrl)))