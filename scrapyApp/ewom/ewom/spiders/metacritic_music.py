import scrapy
import re

class AlbumReviewsSpider(scrapy.Spider):
    name = "albumReviews"
    start_urls = ['https://www.metacritic.com/browse/albums/score/metascore/all']

    #set pagecount limit
    '''custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100
    }'''

    # collect links to album pages and crawl to album detail page
    def parse(self, response):
        relativeUrls = response.css('td.clamp-summary-wrap > a::attr(href)').extract()

        for relativeUrl in relativeUrls:
            yield scrapy.Request(url = response.urljoin(relativeUrl), callback=self.parse_album_details)

        #pagination funtion
        nextPage = response.css('div.page_flipper > span.next > a::attr(href)').get()
        if nextPage:
            yield scrapy.Request(url = response.urljoin(nextPage), callback=self.parse)

    # crawl movie pages and add movie data to data dict
    def parse_album_details(self, response):
        productName = response.css('div.product_title > a > span > h1::text').get()
        type = 'Album'
        metascore = response.css('div.metascore_wrap > a > div > span::text').get()
        userscore = response.css('div.userscore_wrap > a > div::text').get()
        producer = response.css('span.band_name::text').get()
        releaseDate = response.css('div.content_head > div.product_data > ul > li.release > span.data::text').get()
        if response.css('li.product_summary > span.data > span::text').get() != ' ':
            summary = response.css('li.product_summary > span.data > span::text').get()
        else: summary = response.css('li.product_summary > span.data > span > span.blurb_expanded::text').get()
        productUrlSegment = re.findall('music\/(.+)', response.request.url)[0]

        #create dictionary with movie data
        albumData = {
            'productName': productName,
            'type': type,
            'metascore': metascore,
            'userscore': userscore,
            'producer': producer,
            'releaseDate': releaseDate,
            'summary': summary,
            'productUrlSegment': productUrlSegment
        }

        #create data dict with movie data
        data = albumData

        #get link to critic reviews page
        criticReviewPageUrl = response.css('div.metascore_wrap > a::attr(href)').get()

        #crawl to critic review page
        yield scrapy.Request(url = response.urljoin(criticReviewPageUrl), callback=self.parse_album_critic_reviews, meta={'data': data, 'reviews': []})
    
    #crawl critic review page and add review data to data dict
    def parse_album_critic_reviews(self, response):

        #get data and create array for reviews
        data = response.meta['data']
        reviews = response.meta['reviews']

        #collect reviews
        for review in response.css('li.critic_review'):
            if review.css('div.source > a::text').get():
                author = review.css('div.source > a::text').get()
            else: author = review.css('div.source::text').get()
            score = review.css('div.metascore_w::text').get()
            reviewText = review.css('div.review_body::text').get()

            #create dictionary with critic review data
            criticReviewData = {
                'author': author,
                'score': score,
                'reviewText': reviewText
            }

            #add review data to reviews array
            reviews.append(criticReviewData)
        
        #pagination funtion
        nextPage = response.css('div.page_flipper > span.next > a::attr(href)').get()
        if nextPage:
            yield scrapy.Request(url = response.urljoin(nextPage), callback=self.parse_album_critic_reviews, meta={'data': data, 'reviews': reviews})
        
        #add reviews array to data dict
        data.update({'criticReviews': reviews})
        
        #crawl to user review page
        userReviewPageUrl = response.css('div.user_reviews_module > div > div > h2 > a::attr(href)').get()
        yield scrapy.Request(url = response.urljoin(userReviewPageUrl), callback=self.parse_album_user_reviews, meta={'data': data, 'reviews': []})        

    #crawl user review page and add review data to data dict
    def parse_album_user_reviews(self, response):

        #get data and create array for reviews
        data = response.meta['data']
        reviews = response.meta['reviews']

        #collect reviews
        for review in response.css('li.user_review'):
            if review.css('div.name > a::text').get():
                author = review.css('div.name > a::text').get()
            else: author = review.css('div.name > span::text').get()
            dateCreated = review.css('div.date::text').get()
            score = review.css('div.metascore_w::text').get()
            if review.css('div.review_body > span > span.blurb_expanded::text').get():
                reviewText = review.css('div.review_body > span > span.blurb_expanded::text').get()
            else: reviewText = review.css('div.review_body > span::text').get()

            #create dictionary with user review data
            userReviewData = {
                'author': author,
                'dateCreated': dateCreated,
                'score': score,
                'reviewText': reviewText,
            }

            #add review data to reviews array
            reviews.append(userReviewData)
        
        #pagination funtion
        nextPage = response.css('div.page_flipper > span.next > a::attr(href)').get()
        if nextPage:
            yield scrapy.Request(url = response.urljoin(nextPage), callback=self.parse_album_user_reviews, meta={'data': data, 'reviews': reviews})
        else:
            #add reviews array to data dict
            data.update({'userReviews': reviews})

            #yield final data dict
            yield data