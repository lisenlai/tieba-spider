# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TiebaspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class TieItem(scrapy.Item):     # 帖子属性
    tie_id = scrapy.Field()
    author = scrapy.Field()
    title = scrapy.Field()
    time = scrapy.Field()

class FloorItem(scrapy.Item):   # 帖子中楼的属性
    author = scrapy.Field()
    floor_num = scrapy.Field()
    tie_id = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()

class FloorFloorItem(scrapy.Item):  #帖子中楼中楼的属性
    author = scrapy.Field()
    tie_id = scrapy.Field()
    floor_num = scrapy.Field()
    content = scrapy.Field()
    time = scrapy.Field()