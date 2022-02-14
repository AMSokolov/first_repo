from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lesson7.leroymerlin.spiders.leroymerlinru import LeroymerlinSpider
from lesson7.leroymerlin import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroymerlinSpider, query='припой')
    process.start()