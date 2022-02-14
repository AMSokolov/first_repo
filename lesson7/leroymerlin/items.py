# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def process_price(value):          # Функция для обработки цен
    value = value.replace('\xa0', '')
    try:
        return int(value)
    except:
        return value

def process_param(value):
    try:
        value = value.replace('\n', '').replace(' ', '')
    except:
        pass
    if value != '':
        return value

class LeroymerlinItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(process_price), output_processor=TakeFirst())
    photos = scrapy.Field()
    parameters = scrapy.Field(input_processor=MapCompose(process_param))
    url = scrapy.Field()
