# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item,Field


class JusersItem(Item):
    nickname = Field()
    subscriptions = Field()
    fans = Field()
    url = Field()
    articles = Field()
    words = Field()
    likes = Field()
    comments = Field()
    regtime = Field()
    lasttime = Field()
    lastact = Field()

    