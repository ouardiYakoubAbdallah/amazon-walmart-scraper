import scrapy
import logging

from ..items import MyscraperItem

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.com']
    finished = False
    start_urls = [
        'https://www.amazon.com/b?node=16225007011&pf_rd_r=WQHEEXE0WPB1EF03N4VJ&pf_rd_p=e5b0c85f-569c-4c90-a58f-0c0a260e45a0',
    ]

    def start_requests(self):
        url = 'https://www.amazon.com/b?node=16225007011&pf_rd_r=WQHEEXE0WPB1EF03N4VJ&pf_rd_p=e5b0c85f-569c-4c90-a58f-0c0a260e45a0'
        #logging.info('Current page: {}'.format(url))
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        pages = response.css('.pagnDisabled::text').get()
        pages = int(pages) + 1
        for page in range(1,pages):
            page_url = 'https://www.amazon.com/s?rh=n%3A16225007011&page={}&qid=1601492048&ref=lp_16225007011_pg_2'.format(page)
            yield scrapy.Request(url=page_url, callback=self.page_parse)

    def page_parse(self, response):
        logging.info('CURRENT PAGE URL : {}'.format(response.url))
        products = response.css('a.a-link-normal.s-access-detail-page.s-color-twister-title-link.a-text-normal').css('::attr(href)').extract()
        if products == []:
            #product not in the first page
            products = response.css('a.a-link-normal.a-text-normal').css('::attr(href)').extract()
            for pr in products:
                product_url = 'https://www.amazon.com/' + pr
                yield scrapy.Request(url=product_url, callback=self.product_parse)
        else :
            for pr in products:
                yield scrapy.Request(url=pr, callback=self.product_parse)


    def product_parse(self, response):
        item = MyscraperItem()

        logging.info('CURRENT PRODUCT URL : {}'.format(response.url))
        try:
            title = response.css('span#productTitle::text').get() or response.css('.qa-title-text::text').get()
            item['title'] = title.strip()
            item['seller'] = response.css('#sellerProfileTriggerId::text').get() or response.css('span#buyboxTabularTruncate-1').css('::text').get() or 'Currently unavailable'
            item['price'] = response.css('#priceblock_ourprice::text').get() or response.css('#priceblock_dealprice::text').get() or 'Currently unavailable'
            #image = response.css('#altImages ul li img').css('::attr(src)').get()
            image = response.css('div.imgTagWrapper img').css('::attr(data-old-hires)').get()
            item['image'] = image
            yield item
        except AttributeError:
            logging.error('Cannot scrap product')

