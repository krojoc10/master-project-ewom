import scrapy

class GameSalesSpider(scrapy.Spider):
    name = "gameSales"
    start_urls = ['https://www.vgchartz.com/games/games.php?name=&keyword=&console=&region=All&developer=&publisher=&goty_year=&genre=&boxart=Both&banner=Both&ownership=Both&showmultiplat=No&results=200&order=Sales&showtotalsales=0&showtotalsales=1&showpublisher=0&showpublisher=1&showvgchartzscore=0&shownasales=0&showdeveloper=0&showcriticscore=0&showpalsales=0&showreleasedate=0&showuserscore=0&showjapansales=0&showlastupdate=0&showothersales=0&showshipped=0']

    #set pagecount limit
    '''custom_settings = {
        'CLOSESPIDER_PAGECOUNT': 100
    }'''

    #crawl pages and collect sales data
    def parse(self, response):

        #collect title, publisher and sales data
        for dataRecord in response.css('div#generalBody > table > tr')[3:]:
            gameName = dataRecord.css(':nth-child(3) > a::text').get()
            publisher = dataRecord.css(':nth-child(5)::text').get()
            sales = dataRecord.css(':nth-child(6)::text').get()

            #yield data record
            yield {
                'gameName': gameName,
                'publisher': publisher,
                'sales': sales
            }
        
        #pagination funtion
        try:
            nextPage = response.xpath('//a[@class="selected"]/./following-sibling::span/a').attrib['href']
        except:
            nextPage = response.xpath('//a[@class="selected"]/../following-sibling::span/a').attrib['href']
        if response.xpath('//a[@class="selected"]').attrib['href'] != nextPage:
            yield scrapy.Request(url = response.urljoin(nextPage), callback=self.parse)