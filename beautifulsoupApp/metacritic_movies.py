from urllib import request
from bs4 import BeautifulSoup
import json
import re
import ssl
import certifi
import datetime

#function to open page and create soup
def getSoup(url):
    req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    pageContent = request.urlopen(req, context=ssl.create_default_context(cafile=certifi.where())).read()
    return BeautifulSoup(pageContent, 'html.parser')

#function to extract urls for movie detail pages
def extractMovieDetailsUrl(movieDetailsUrls, soup):

    #get all a tag elements with link to movie detail page
    movieDetailsUrlElements = soup.select('a.title')

    #extract urls from a tag elements
    for movieDetailsUrlElement in movieDetailsUrlElements:
        movieDetailsUrls.append('https://www.metacritic.com' + movieDetailsUrlElement['href'])

    return movieDetailsUrls

#function to extract critic reviews
def extractCriticReviews(reviews, soup):

    #collect reviews
    for review in soup.select('div.review'):
        try:
            if review.has_attr('id'):
                continue
            else:
                if review.select('span.author'):
                    if review.select('span.author a'):
                        author = review.select('span.author')[0].find('a').get_text()
                    else: author = review.find('span', class_='author').get_text()
                else: author = ''
                score = review.find('div', class_='metascore_w').get_text()
                if review.select('div.summary a'):
                    reviewText = review.select('div.summary')[0].find('a').get_text()
                else: reviewText = review.find('div', class_='summary').get_text()

                #create dictionary with critic review data
                criticReviewData = {
                    'author': author,
                    'score': score,
                    'reviewText': reviewText
                }

                #add review data to reviews array
                reviews.append(criticReviewData)
        except: 
            print('Review not scrapeable: ' + review)
            continue
    
    return reviews

#function to extract user reviews
def extractUserReviews(reviews, soup):

    #collect reviews
    for review in soup.select('div.review'):
        try:
            if review.select('span.author'):
                if review.select('span.author a'):
                    author = review.select('span.author')[0].find('a').get_text()
                else: author = review.find('span', class_='author').get_text()
            else: author = ''
            dateCreated = review.find('span', class_='date').get_text()
            score = review.find('div', class_='metascore_w').get_text()
            if review.select('div.summary div')[0].find('span').get_text() != ' ':
                reviewText = review.select('div.summary div')[0].find('span').get_text()
            else: reviewText = review.select('div.summary div span')[0].find('span', class_='blurb_expanded').get_text()

            #create dictionary with critic review data
            userReviewData = {
                'author': author,
                'dateCreated': dateCreated,
                'score': score,
                'reviewText': reviewText
            }

            #add review data to reviews array
            reviews.append(userReviewData)
        except: 
            print('Review not scrapeable: ' + review)
            continue
    
    return reviews

#main function to extract data
def extractData(soup):
    productName = soup.select('div.product_page_title')[0].find('h1').get_text()
    type = 'Movie'
    metascore = soup.select('div.ms_wrapper table tr td.summary_right a')[0].find('span').get_text()
    userscore = soup.select('div.user_score_summary table tr td.summary_right a')[0].find('span').get_text()
    producer = soup.select('span.distributor')[0].find('a').get_text()
    summary = soup.select('div.summary_deck span')[1].find('span').get_text()
    productUrlSegment = re.findall('movie\/(.+)', soup.find('meta', property='og:url')['content'])[0]

    #create dictionary with movie data
    data = {
        'productName': productName,
        'type': type,
        'metascore': metascore,
        'userscore': userscore,
        'producer': producer,
        'summary': summary,
        'productUrlSegment': productUrlSegment
    }

    #get link to critic reviews page, extract reviews, and add them to data dict with loop for pagination
    criticReviews = []
    soup = getSoup('https://www.metacritic.com' + soup.select('div.ms_wrapper div.header_title')[0].find('a')['href'])
    
    while True:
        criticReviews = extractCriticReviews(criticReviews, soup)

        #get pagination element
        nextPage = soup.select('div.page_flipper span.next')

        #go to next page if available
        if nextPage:
            if nextPage[0].find('a'):
                nextPage = 'https://www.metacritic.com' + nextPage[0].find('a')['href']
                soup = getSoup(nextPage)
            #exit if next page is not available
            else: break
        else: break
        
    data.update({'criticReviews': criticReviews})

    #get link to user reviews page, extract reviews, and add them to data dict with loop for pagination
    userReviews = []
    soup = getSoup('https://www.metacritic.com' + soup.select('p.score_user')[0].find('a')['href'])
    
    while True:
        userReviews = extractUserReviews(userReviews, soup)
        #get pagination element
        nextPage = soup.select('div.page_flipper span.next')

        #go to next page if available
        if nextPage:
            if nextPage[0].find('a'):
                nextPage = 'https://www.metacritic.com' + nextPage[0].find('a')['href']
                soup = getSoup(nextPage)
            #exit if next page is not available
            else: break
        else: break
    
    data.update({'userReviews': userReviews})
    print('item scraped: ', data['productUrlSegment'])
    
    return data

#starting
startTime = datetime.datetime.now()
print(startTime.strftime("%m/%d/%Y, %H:%M:%S") + ', status: started')

#empty list to save urls to movie details pages in
movieDetailsUrls = []

#create soup with inital url
soup = getSoup('https://www.metacritic.com/browse/movies/score/metascore/all')

#get urls to movie detail pages with loop for pagination
print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ', status: collecting urls to movie detail pages')

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
        print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ', status: urls to movie detail pages successfully gathered')
        break

#create empty data list
data = []

itemCount = 1
#extract data
for movieDetailsUrl in movieDetailsUrls:
    try:
        data.append(extractData(getSoup(movieDetailsUrl)))
        print('# of items scraped: ' + str(itemCount))
        itemCount = itemCount + 1
    except:
        print('Movie not scrapeable: ' + movieDetailsUrl)
        continue

#finishing
finishTime = datetime.datetime.now()
print(finishTime.strftime("%m/%d/%Y, %H:%M:%S") + ', status: finished')
elapsedTime = datetime.timedelta.total_seconds(finishTime - startTime)

#update and print stats
stats = {
    'start_time': startTime,
    'finish_time': finishTime,
    'elapsed_time_seconds': elapsedTime,
    'item_scraped_count': len(data)
    }

print(stats)

#convert data into json and write it to file
json_object = json.dumps(data)
with open("metacritic-beautifulsoup-data.json", "w") as outfile:
    outfile.write(json_object)