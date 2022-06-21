"""Define here the models for your scraped items"""


import scrapy


class GeneralInformationItem(scrapy.Item):
    """
    define scrapy general information items for our spider
    """

    company_url = scrapy.Field()
    status = scrapy.Field()
    languages = scrapy.Field()
    tagged_by_b2b_words = scrapy.Field()
    payments = scrapy.Field()
    webshop_urls = scrapy.Field()
    webshop_system = scrapy.Field()
    wappalyzer = scrapy.Field()
    social_media = scrapy.Field()


class PriceItem(scrapy.Item):
    """
    define scrapy price items for our spider
    """

    company_url = scrapy.Field()
    products_quantity = scrapy.Field()
    products_avg_price = scrapy.Field()
    currency = scrapy.Field()


class ContactItem(scrapy.Item):
    """
    define scrapy contact information items for our spider
    """

    company_url = scrapy.Field()
    phone = scrapy.Field()
    contact_information_url = scrapy.Field()
    email = scrapy.Field()
