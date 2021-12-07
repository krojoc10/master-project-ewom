import scrapy

class MovieSalesSpider(scrapy.Spider):
    name = "movieSales"
    start_urls = ['https://www.boxofficemojo.com/chart/ww_top_lifetime_gross/']

    #set pagecount limit
    '''custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100
    }'''

    #crawl pages and collect sales data
    def parse(self, response):

        #collect title and sales data
        for dataRecord in response.css('#table > div > table > tr'):
            movieName = dataRecord.css('td.mojo-field-type-title > a::text').get()
            sales = dataRecord.css('td.mojo-field-type-money::text').get()

            #yield data record
            yield {
                'movieName': movieName,
                'sales': sales
            }
        
        #pagination funtion
        nextPage = response.css('div.mojo-pagination > ul > li.a-last > a::attr(href)').get()
        if nextPage:
            yield scrapy.Request(url = response.urljoin(nextPage), callback=self.parse)