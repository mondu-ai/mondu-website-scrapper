"""Define here the models for your scraped items"""


import scrapy


class MonduWebsiteScrapperItem(scrapy.Item):
    """
    define scrapy items for our spider
    """

    company_url = scrapy.Field()
    languages = scrapy.Field()
    tagged_as_b2b = scrapy.Field()
    tagged_by_b2b_words = scrapy.Field()
    payments = scrapy.Field()
    webshop_urls = scrapy.Field()
    webshop_system = scrapy.Field()
    products_quantity = scrapy.Field()
    products_avg_price = scrapy.Field()
    wappalyzer = scrapy.Field()


# class MonduItemLoader(ItemLoader):
#     """_summary_

#     Args:
#         ItemLoader (_type_): _description_
#     """

#     wappalyzer_in = scrapy.Field(
#         input_processor=MapCompose(extract_categories_from_wappalyzer), serializer=dict
#     )
