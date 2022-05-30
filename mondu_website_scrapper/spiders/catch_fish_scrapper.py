""" Define scraper spider"""
import ast
import logging
import re
from typing import Any, Dict, List, Union
import pathlib
import pandas as pd
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.project import get_project_settings
from Wappalyzer import Wappalyzer, WebPage
from mondu_website_scrapper.items import MonduWebsiteScrapperItem

wappalyzer = Wappalyzer.latest()
# pylint: disable=R0201


class LeadSpider(scrapy.Spider):
    """
    our first spider for crawling web pages.


    Returns: return a csv file
    Yields: yeild an item and item pipeline will export it as a csv file
    """

    name = "findingnemo"

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }

    def __init__(self):
        super().__init__()
        self.link_url_extractor = LinkExtractor(allow="cart|shop|online", unique=True)
        self.link_text_extractor = LinkExtractor(
            restrict_text=[
                "shop",
                "cart",
                "Warenkorb",
                "Einkaufswagen",
                "Checkout",
                "Jetzt bezahlen",
                "Zahlungsmethoden",
                "Zahlungsarten",
            ],
            unique=True,
        )
        self.extract_links = []
        self.item = MonduWebsiteScrapperItem()

    def start_requests(self):
        urls = [
            "https://luma-handel.at/",
            "https://zpnevolution.com/",
            "https://www.psa-online.at/",
            "https://www.zentrada.com/de/",
            "https://bwe.co.at/",
            "https://tropextrakt.com/en/",
            "https://www.klosterkitchen.de/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):  # pylint: disable=arguments-differ
        """
        the parse method inherited from scrapy.Spider. overwrite it with our own returns.

        Yields: item, in a python dict format, containes scraped information.
        """
        self.item["company_url"] = response.url
        languages = response.css("html").xpath("@lang")
        for lang in languages:
            self.item["languages"] = lang.get()
        self.item["webshop_urls"] = self.extract_webshop_url(response)
        self.item["payments"] = self.extract_payments(response)
        self.item["tagged_by_b2b_words"] = self.extract_b2b_keywords(response)
        self.item["products_avg_price"] = self.extract_price_info(response)[
            "products_avg_price"
        ]
        self.item["products_quantity"] = self.extract_price_info(response)[
            "products_quantity"
        ]
        self.item["webshop_system"] = self.extract_webshop_system(response)

        self.item["wappalyzer"] = self.extract_wappalyzer_data(response)

        yield self.item

    def extract_webshop_url(self, response) -> List:
        """
        extract links that contains keywords related to webshop

        Returns: a list of links
        """
        self.extract_links = list(
            set(
                self.link_url_extractor.extract_links(response)
                + self.link_text_extractor.extract_links(response)
            )
        )
        if self.extract_links:
            return [link.url for link in self.extract_links]
        return [link.url for link in LinkExtractor().extract_links(response)]

    def parse_payments(self, response) -> scrapy.http.response:
        """
        parse payments from all extracted links and followed response.
        look up payment keywords on html body of extracted links.

        Yields: response
        """
        for link in LinkExtractor().extract_links(response):
            self.logger.info("Extract payment methods from %s...", link.url)
            yield response.follow(link.url, callback=self.extract_payments)

    def extract_payments(self, response) -> List:
        """
        extract payments by looking up pre-defined payments keyword

        Returns: a list of payments if keywords are matched, otherwise return empty list
        """
        payments_keywords = self.settings["PAYMENTS_KEYWORDS"]

        res_alt = [
            word.lower() for word in response.xpath("//img/@alt").getall() if word
        ]
        res_src = [
            word.lower() for word in response.xpath("//img/@src").getall() if word
        ]

        return list(
            set(
                pay
                for scrapped_src in res_alt + res_src
                for pay in payments_keywords
                if pay in scrapped_src
            )
        )

    def parse_b2b_keywords(
        self, response: scrapy.http.response
    ) -> scrapy.http.response:
        """
        extract links and followed the response with links.
        extract b2b related words from html body of extracted links

        Yields: response object
        """
        for link in LinkExtractor().extract_links(response):
            self.logger.info("Extract b2b words from link %s...", link.url)
            yield response.follow(link.url, callback=self.extract_b2b_keywords)

    def extract_b2b_keywords(self, response: scrapy.http.response) -> List:
        """
        extract bb2 keywords pre-defined under settings.py from html body

        Returns: a list of b2b keywords if they are presented
        """
        b2b_keywords = self.settings["B2B_KEYWORDS"]

        data = response.body.decode("utf-8").lower()
        b2b_key_dict = {}
        for word in b2b_keywords:
            if re.search(word, data) is not None:
                b2b_key_dict[word] = True
            else:
                b2b_key_dict[word] = False
        if any(value is True for value in b2b_key_dict.values()):
            self.item["tagged_as_b2b"] = True
        else:
            self.item["tagged_as_b2b"] = False

        return [k for k, v in b2b_key_dict.items() if v]

    def parse_products(self, response: scrapy.http.response) -> scrapy.http.response:
        """
        extract links with allowed words which might direct us to products' pages.
        followed extracted link and extract price information from it.

        Yields: reponse object
        """
        for link in LinkExtractor(
            allow="collection|product|produkte|kategories|categories", unique=True
        ).extract_links(response):
            self.logger.info("Extract price from a product link %s...", link.url)
            yield response.follow(link.url, callback=self.extract_price_info)

    def extract_price_info(self, response: scrapy.http.response) -> Dict:
        """
        extract price information by matching any numeric up to 10 digits before and after
        decimal indicator comma or dot for currency € and $

        Returns: A dict with keys of products_avg_price and products_quantity
        """
        data = response.body.decode("utf-8")
        price_lst = re.findall(r"\d{1,10}[\,\.]\d{1,10}(?=.*[€|$])", data)
        price_lst = [float(p.strip().replace(",", ".")) for p in price_lst]

        return {
            "products_avg_price": round(sum(price_lst) / len(price_lst), 2)
            if price_lst
            else None,
            "products_quantity": len(price_lst),
        }

    def parse_webshop_system(
        self, response: scrapy.http.response
    ) -> scrapy.http.response:
        """
        parse the webshop system and follow the response.
        extract webshop system by pre-defined keywords given by market team.

        Returns: yield a response
        """
        for link in LinkExtractor().extract_links(response):
            self.logger.info("Extract payment methods from %s...", link.url)
            yield response.follow(link.url, callback=self.extract_webshop_system)

    def extract_webshop_system(self, response: scrapy.http.response) -> List:
        """_summary_

        Args:
            response (_type_): _description_
        """
        webshop_sys = []
        websystem_keywords = self.settings["WEBSYSTEMS_KEYWORDS"]
        websystem_keywords = [i.lower() for i in websystem_keywords]
        data = response.body.decode("utf-8").lower()
        for word in websystem_keywords:
            if re.search(word, data) is not None:
                webshop_sys.append(word)
        return webshop_sys

    def parse_wappalyzer_data(
        self, response: scrapy.http.response
    ) -> scrapy.http.response:
        """
        parse wappalyzer data

        Yields: a response
        """

        for link in self.extract_links:
            self.logger.info("wappalyzing data from %s...", link)
            yield response.follow(link, callback=self.extract_wappalyzer_data)

    def extract_wappalyzer_data(
        self, response: scrapy.http.response
    ) -> Dict[str, Dict[str, Any]]:
        """
        using wappalyzer api extract info

        returns: dict
        """
        webpage = WebPage.new_from_url(response.url)
        return wappalyzer.analyze_with_categories(webpage)


def create_report_dataset(
    read_file_path: Union[str, pathlib.Path] = None,
    wappalyzer_data_column: str = "wappalyzer",
):
    """
    create final report for scrapped results
    1. assume we will always have wappalyzer data in the column as this is the part of the pipeline.
    this part of data is normalized and then converted from a pandas series of dict into columns
    2. the report is saved under default result folder with the surffix __report

    Returns: None
    """
    if read_file_path is None:
        read_file_path = settings["FILE_FOLDE"] / f"{LeadSpider.name}.csv"
    save_file_path = settings["FILE_FOLDE"] / f"{LeadSpider.name}__report.csv"

    scraped_df = pd.read_csv(read_file_path)
    logging.info("scraped dataframe is of %s", scraped_df.shape)

    wappalyzer_df = normalize_wappalyzer_data(scraped_df[wappalyzer_data_column])
    scraped_df.drop(wappalyzer_data_column, inplace=True, axis=1)
    update_df = pd.concat([scraped_df, wappalyzer_df], axis=1)
    update_df.to_csv(save_file_path, index=False)
    logging.info("final report dataframe is of %s", update_df.shape)
    logging.info("final report csv is saved under %s", save_file_path)


def normalize_wappalyzer_data(wappalyzer_data: pd.Series) -> pd.DataFrame:

    """
    normalize the result of wappalyzed api data and create a pandas dataframe
    1. convert to json
    2.apply json normalize to the whole column

    Returns: a pandas dataframe
    """
    wappalyzer_data.apply(lambda x: x.replace("'", '"'))

    return pd.json_normalize(wappalyzer_data.apply(ast.literal_eval).tolist())


if __name__ == "__main__":
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(LeadSpider)
    process.start()
    create_report_dataset()
