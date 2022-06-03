"""Define here the models for your scraped items"""


import scrapy
from itemloaders.processors import Join


class GeneralInformationItem(scrapy.Item):
    """
    define scrapy general information items for our spider
    """

    company_url = scrapy.Field()
    languages = scrapy.Field()
    tagged_as_b2b = scrapy.Field()
    tagged_by_b2b_words = scrapy.Field(output_processor=Join(", "))
    payments = scrapy.Field()
    webshop_urls = scrapy.Field()
    webshop_system = scrapy.Field()
    wappalyzer = scrapy.Field()


class PriceItem(scrapy.Item):
    """
    define scrapy price items for our spider
    """

    company_url = scrapy.Field()
    products_quantity = scrapy.Field()
    products_avg_price = scrapy.Field()
    currency = scrapy.Field()
