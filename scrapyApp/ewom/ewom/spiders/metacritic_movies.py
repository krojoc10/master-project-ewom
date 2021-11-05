import scrapy

class MovieReviewsSpider(scrapy.Spider):
    name = "movieReviews"
    start_url = 'https://www.metacritic.com/browse/movies/score/metascore/all'

    # collect links to movie pages and crawl to movie detail page
    def parse(self, response):
        relativeUrls = response.css('td.clamp-summary-wrap > a::attr(href)').extract()

        for relativeUrl in relativeUrls:
            yield scrapy.Request(url = response.urljoin(relativeUrl), callback=self.parse_details_movie)

    def parse_details_movie(self, response):
        Name = response.css('div.product_page_title > h1::text').get()