import scrapy
from scrapy.http import HtmlResponse
from lesson7.leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, query, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://leroymerlin.ru/search/?q={query}']

    def parse(self, response: HtmlResponse):
        adv_links = response.xpath("//a[@data-qa-product-name]/@href")
        next_page = response.xpath("//a[contains(@aria-label, 'Следующая страница')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        for link in adv_links:
            yield response.follow(link, callback=self.parse_adv)

    def parse_adv(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('photos', "//img[@alt='product image']/@src")
        loader.add_value('url', response.url)
        loader.add_xpath('parameters', "//div[@class='def-list__group']//text()")
        yield loader.load_item()
