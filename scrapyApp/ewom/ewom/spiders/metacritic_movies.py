import scrapy
import re

class MovieReviewsSpider(scrapy.Spider):
    name = "movieReviews"
    start_urls = ['https://www.metacritic.com/browse/movies/score/metascore/all']

    #set pagecount limit
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100
    }

    # collect links to movie pages and crawl to movie detail page
    def parse(self, response):
        relativeUrls = response.css('td.clamp-summary-wrap > a::attr(href)').extract()

        for relativeUrl in relativeUrls:
            yield scrapy.Request(url = response.urljoin(relativeUrl), callback=self.parse_movie_details)

        #pagination funtion
        nextPage = response.css('div.page_flipper > span.next > a::attr(href)').get()
        if nextPage:
            yield scrapy.Request(url = response.urljoin(nextPage), callback=self.parse)

    # crawl movie pages and collect data
    def parse_movie_details(self, response):
        productName = response.css('div.product_page_title > h1::text').get()
        type = 'Movie'
        metascore = response.css('div.ms_wrapper > table > tr > td.summary_right > a > span::text').get()
        userscore = response.css('div.user_score_summary > table > tr > td.summary_right > a > span::text').get()
        producer = response.css('span.distributor > a::text').get()
        summary = response.css('div.summary_deck span > span::text').get()
        productUrlSegment = re.findall('movie\/(.+)', response.request.url)[0]

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

        #yield movieData

        #get link to critic and user reviews page
        reviewPageUrls = response.css('div.reviews > div > div > a.see_all::attr(href)').extract()
        criticReviewPageUrl = reviewPageUrls[0]

        #crawl to critic review page
        yield scrapy.Request(url = response.urljoin(criticReviewPageUrl), callback=self.parse_movie_critic_reviews)

        try:
            userReviewPageUrl = reviewPageUrls[1]
            #crawl to user review page
            yield scrapy.Request(url = response.urljoin(userReviewPageUrl), callback=self.parse_movie_user_reviews)
        except: print(productUrlSegment + " has no user reviews")
    
    #crawl critic review page and collect review data
    def parse_movie_critic_reviews(self, response):
        for review in response.css('div.review'):
            type = 'critic'
            if review.css('span.author > a::text').get():
                author = review.css('span.author > a::text').get()
            else: author = review.css('span.author::text').get()
            score = review.css('div.metascore_w::text').get()
            if review.css('div.summary > a::text').get():
                summary = review.css('div.summary > a::text').get()
            else: summary = review.css('div.summary::text').get()
            productUrlSegment = re.findall('movie\/(.+)\/', response.request.url)[0]

            #create dictionary with critic review data
            criticReviewData = {
                'type': type,
                'author': author,
                'score': score,
                'summary': summary,
                'productUrlSegment': productUrlSegment
            }

            yield criticReviewData

    #crawl user review page and collect review data
    def parse_movie_user_reviews(self, response):
        for review in response.css('div.review'):
            type = 'user'
            if review.css('span.author > a::text').get():
                author = review.css('span.author > a::text').get()
            else: author = review.css('span.author::text').get()
            dateCreated = review.css('span.date::text').get()
            score = review.css('div.metascore_w::text').get()
            if review.css('div.summary > div > span::text').get() is not ' ':
                summary = ' '.join(review.css('div.summary > div > span::text').extract())
            else: summary = ' '.join(review.css('div.summary > div > span > span.blurb_expanded::text').extract())
            productUrlSegment = re.findall('movie\/(.+)\/', response.request.url)[0]

            #create dictionary with user review data
            userReviewData = {
                'type': type,
                'author': author,
                'dateCreated': dateCreated,
                'score': score,
                'summary': summary,
                'productUrlSegment': productUrlSegment
            }

            #yield userReviewData