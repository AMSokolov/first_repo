import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vakansii/programmist.html?geo%5Bt%5D%5B0%5D=4&click_from=facet',
                  'https://www.superjob.ru/vakansii/programmist.html?geo%5Br%5D%5B0%5D=3&click_from=facet'
                  ]

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath("//a[contains(@class, 'f-test-link-Dalshe')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//div[contains(@class, 'vacancy-item')]//a[contains(@href, 'vakansii')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    @staticmethod
    def vacancy_parse(response: HtmlResponse):
        name = response.xpath("//h1//text()").get()
        salary = response.xpath("///span[contains(@class,'_2Wp8I _3a-0Y _3DjcL _3fXVo')]//text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
