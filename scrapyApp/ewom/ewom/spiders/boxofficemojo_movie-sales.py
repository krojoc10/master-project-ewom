import scrapy
import re

class MovieSalesSpider(scrapy.Spider):
    name = "movieSales"
    start_urls = ['https://www.boxofficemojo.com/year/world/2022/']

    #set pagecount limit
    '''custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100
    }'''

    #crawl pages and collect sales data
    def parse(self, response):

        #collect title and sales data
        dataRecords = response.css('#table > div > table > tr')
        dataRecords = dataRecords[1:]
        releaseYear = re.findall('\d+', response.request.url)[0]

        for dataRecord in dataRecords:
            movieName = dataRecord.css('td:nth-of-type(2n) > a::text').get()
            sales = dataRecord.css('td:nth-of-type(3n)::text').get()

            #yield data record
            yield {
                'movieName': movieName,
                'releaseYear': releaseYear,
                'sales': sales
            }
        
        #pagination funtion
        if releaseYear != '1977':
            yield scrapy.Request(url = 'https://www.boxofficemojo.com/year/world/' + str(int(releaseYear) - 1), callback=self.parse)