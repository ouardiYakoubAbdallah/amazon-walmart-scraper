import scrapy
import logging

from ..items import MyscraperItem

class WalmartSpider(scrapy.Spider):
    name = 'walmart'
    allowed_domains = ['walmart.com']
    start_urls = [
        'https://www.walmart.com/browse/computers/3944_3951'
    ]
    def start_requests(self):
        url='https://www.walmart.com/browse/computers/3944_3951'
        #logging.info('Current page: {}'.format(url))
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for page in range(1,26):
            page_url = 'https://www.walmart.com/browse/computers/3944_3951?page={}'.format(page)
            yield scrapy.Request(url=page_url, callback=self.page_parse)

    def page_parse(self, response):
        products = response.css('.truncate-title::attr(href)').extract()
        for pr in products:
            product_url = 'https://www.walmart.com' + pr
            yield scrapy.Request(url=product_url, callback=self.product_parse)

    def product_parse(self, response):
        item = MyscraperItem()

        logging.info('CURRENT PAGE : {}'.format(response.url))

        item['title'] = response.css('.prod-productTitle-buyBox::text').get()
        item['seller'] = response.css('.seller-name::text').get()
        item['price'] = response.css('.price--stylized .visuallyhidden').css('::text').get()
        item['image'] = response.css('.prod-hero-image-image').css('::attr(src)').get() or response.css('.hover-zoom-hero-image').css('::attr(src)').get()

        yield item