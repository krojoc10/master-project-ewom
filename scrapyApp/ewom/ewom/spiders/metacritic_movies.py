import scrapy
import re

class MovieReviewsSpider(scrapy.Spider):
    name = "movieReviews"
    start_urls = ['https://www.metacritic.com/browse/movies/score/metascore/all']

    #set pagecount limit and autothrottle
    custom_settings = {
        #'CLOSESPIDER_PAGECOUNT': 100,
        'AUTOTHROTTLE_ENABLED': True
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

    # crawl movie pages and add movie data to data dict
    def parse_movie_details(self, response):
        productName = response.css('div.product_page_title > h1::text').get()
        type = 'Movie'
        metascore = response.css('div.ms_wrapper > table > tr > td.summary_right > a > span::text').get()
        userscore = response.css('div.user_score_summary > table > tr > td.summary_right > a > span::text').get()
        producer = response.css('span.distributor > a::text').get()
        releaseDate = response.css('span.release_date > span:nth-of-type(2n)::text').get()
        if response.css('div.summary_deck > span > span::text').get() != ' ':
            summary = response.css('div.summary_deck > span > span::text').get()
        else: summary = response.css('div.summary_deck > span > span > span.blurb_expanded::text').get()
        rankings = response.css('table.rankings > tr > td.ranking_wrap > div.ranking_title > a::text').getall()
        director = response.css('div.director > a > span::text').get()
        genres = response.css('div.genres > span:nth-of-type(2n) > span::text').getall()
        if response.css('div.rating > span:nth-of-type(2n)::text').get():
            rating = response.css('div.rating > span:nth-of-type(2n)::text').get().strip(' \n\t')
        else: rating = None
        runtime = response.css('div.runtime > span:nth-of-type(2n)::text').get()
        productUrlSegment = re.findall('movie\/(.+)', response.request.url)[0]

        #create dictionary with movie data
        movieData = {
            'productName': productName,
            'type': type,
            'metascore': metascore,
            'userscore': userscore,
            'producer': producer,
            'releaseDate': releaseDate,
            'summary': summary,
            'rankings': rankings,
            'director': director,
            'genres': genres,
            'rating': rating,
            'runtime': runtime,
            'productUrlSegment': productUrlSegment
        }

        #create data dict with movie data
        data = movieData

        #get link to critic reviews page
        criticReviewPageUrl = response.css('div.ms_wrapper > table > tr > td > div.header_title > a::attr(href)').get()

        #crawl to critic review page
        yield scrapy.Request(url = response.urljoin(criticReviewPageUrl), callback=self.parse_movie_critic_reviews, meta={'data': data, 'reviews': []})
    
    #crawl critic review page and add review data to data dict
    def parse_movie_critic_reviews(self, response):

        #get data and create array for reviews
        data = response.meta['data']
        reviews = response.meta['reviews']

        #collect reviews
        for review in response.css('div.review'):
            if review.css('script'):
                continue
            if review.css('span.author > a::text').get():
                author = review.css('span.author > a::text').get()
            else: author = review.css('span.author::text').get()
            score = review.css('div.metascore_w::text').get()
            if review.css('div.summary > a::text').get():
                reviewText = review.css('div.summary > a::text').get().strip(' \n\t')
            else: reviewText = review.css('div.summary::text').get().strip(' \n\t')

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
            yield scrapy.Request(url = response.urljoin(nextPage), callback=self.parse_movie_critic_reviews, meta={'data': data, 'reviews': reviews})
        
        #add reviews array to data dict
        data.update({'criticReviews': reviews})
        
        #crawl to user review page
        userReviewPageUrl = response.css('p.score_user > a::attr(href)').extract_first()
        yield scrapy.Request(url = response.urljoin(userReviewPageUrl), callback=self.parse_movie_user_reviews, meta={'data': data, 'reviews': []})        

    #crawl user review page and add review data to data dict
    def parse_movie_user_reviews(self, response):

        #get data and create array for reviews
        data = response.meta['data']
        reviews = response.meta['reviews']

        #collect reviews
        for review in response.css('div.review'):
            if review.css('span.author > a::text').get():
                author = review.css('span.author > a::text').get()
            else: author = review.css('span.author::text').get()
            dateCreated = review.css('span.date::text').get()
            score = review.css('div.metascore_w::text').get()
            if review.css('div.summary > div > span::text').get() != ' ':
                reviewText = ' '.join(review.css('div.summary > div > span::text').extract())
            else: reviewText = ' '.join(review.css('div.summary > div > span > span.blurb_expanded::text').extract())
            helpfulness = review.css('div.helpful > div > span > span.yes_count::text').get() + '/' + review.css('div.helpful > div > span > span.total_count::text').get()

            #create dictionary with user review data
            userReviewData = {
                'author': author,
                'dateCreated': dateCreated,
                'score': score,
                'reviewText': reviewText,
                'helpfulness': helpfulness
            }

            #add review data to reviews array
            reviews.append(userReviewData)
        
        #pagination funtion
        nextPage = response.css('div.page_flipper > span.next > a::attr(href)').get()
        if nextPage:
            yield scrapy.Request(url = response.urljoin(nextPage), callback=self.parse_movie_user_reviews, meta={'data': data, 'reviews': reviews})
        else:
            #add reviews array to data dict
            data.update({'userReviews': reviews})

            #yield final data dict
            yield data