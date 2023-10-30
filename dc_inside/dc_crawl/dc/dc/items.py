
# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DcItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()
    date = scrapy.Field()
    views = scrapy.Field()
    recommend = scrapy.Field()
    link = scrapy.Field()
    article_no = scrapy.Field()

