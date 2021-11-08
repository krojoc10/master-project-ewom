import scrapy

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
        Name = response.css('div.product_page_title > h1::text').get()
        Type = 'Movie'
        Metascore = response.css('div.ms_wrapper > table > tr > td.summary_right > a > span::text').get()
        Userscore = response.css('div.user_score_summary > table > tr > td.summary_right > a > span::text').get()
        Producer = response.css('span.distributor > a::text').get()
        Summary = response.css('div.summary_deck span > span::text').get()

        #create dictionary with movie data
        movieData = {
            'name': Name,
            'type': Type,
            'metascore': Metascore,
            'userscore': Userscore,
            'producer': Producer,
            'summary': Summary
        }

        #yield movieData

        #get link to critic and user reviews page
        reviewPageUrls = response.css('div.reviews > div > div > a.see_all::attr(href)').extract()
        criticReviewPageUrl = reviewPageUrls[0]
        userReviewPageUrl = reviewPageUrls[1]

        #crawl to critic review page
        yield scrapy.Request(url = response.urljoin(criticReviewPageUrl), callback=self.parse_movie_critic_reviews)

        #crawl to user review page
        yield scrapy.Request(url = response.urljoin(userReviewPageUrl), callback=self.parse_movie_user_reviews)
    
    #crawl critic review page and collect review data
    def parse_movie_critic_reviews(self, response):
        for review in response.css('div.review'):
            Type = 'critic'
            if review.css('span.author > a::text').get():
                Author = review.css('span.author > a::text').get()
            else: Author = review.css('span.author::text').get()
            Score = review.css('div.metascore_w::text').get()
            Summary = review.css('div.summary > a::text').get()

            #create dictionary with critic review data
            criticReviewData = {
                'type': Type,
                'author': Author,
                'score': Score,
                'summary': Summary
            }

            #yield criticReviewData

    #crawl user review page and collect review data
    def parse_movie_user_reviews(self, response):
        for review in response.css('div.review'):
            Type = 'user'
            Author = review.css('span.author > a::text').get()
            DateCreated = review.css('span.date::text').get()
            Score = review.css('div.metascore_w::text').get()
            if review.css('div.summary > div > span::text').get() is not ' ':
                Summary = ' '.join(review.css('div.summary > div > span::text').extract())
            else: Summary = ' '.join(review.css('div.summary > div > span > span.blurb_expanded::text').extract())

            #create dictionary with user review data
            userReviewData = {
                'type': Type,
                'author': Author,
                'dateCreated': DateCreated,
                'score': Score,
                'summary': Summary
            }

            yield userReviewData

#self = MovieReviewsSpider()