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
from mondu_website_scrapper.items import GeneralInformationItem, PriceItem

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
    start_urls = [
        "https://shop.headon.at/",
        "https://pewag.com",
        "https://b2b.fischersports.com/en-us/profile/login",
        "https://www.die-verpackungs-druckerei.de/",
        "https://www.microsoft.com/de-at",
        "https://www.giesswein.com/",
        "https://b2b.vitrasan.com/",
        "https://zpnevolution.com/",
        "https://www.mysortimo.at/de_AT/",
    ]

    def parse(self, response):  # pylint: disable=arguments-differ
        """
        the parse method inherited from scrapy.Spider. overwrite it with our own returns.

        Yields: item, in a python dict format, containes scraped information.
        """
        item = GeneralInformationItem()
        item["company_url"] = response.url
        languages = response.css("html").xpath("@lang")
        for lang in languages:
            item["languages"] = lang.get()

        item["webshop_urls"] = self.extract_webshop_url(response)
        item["payments"] = self.extract_payments(response)
        item["webshop_system"] = self.extract_webshop_system(response)
        item["tagged_by_b2b_words"] = self.extract_b2b_keywords(response)
        item["wappalyzer"] = self.extract_wappalyzer_data(response)
        link_prod_extractor = LinkExtractor(
            allow=f"{response.url}.*(collection|product|produkte|kategories|categories)",
            unique=True,
        )
        for link in link_prod_extractor.extract_links(response):
            print("sending request to product page...")
            yield scrapy.Request(
                link.url,
                callback=self.extract_price_info,
                cb_kwargs={"company_url": response.url},
            )
        yield item

    def extract_webshop_url(self, response) -> List:
        """
        extract links that contains keywords related to webshop

        Returns: a list of links
        """
        link_url_extractor = LinkExtractor(
            allow=f"{response.url}.*(cart|shop|online)", unique=True
        )

        link_text_extractor = LinkExtractor(
            restrict_text=[
                "shop",
                "cart",
                "Warenkorb",
                "Einkaufswagen",
                "Checkout",
                "Jetzt bezahlen",
                "Zahlungsarten",
            ],
            unique=True,
        )

        webshop_links = list(
            set(
                link_url_extractor.extract_links(response)
                + link_text_extractor.extract_links(response)
            )
        )

        if webshop_links:
            return [link.url for link in webshop_links]
        return []

    def extract_payments(self, response: scrapy.http.response) -> List:
        """
        extract payments by looking up pre-defined payments keyword

        Returns: a list of payments if keywords are matched, otherwise return empty list
        """

        payments_keywords = self.settings["PAYMENTS_KEYWORDS"]

        res_payment = [
            word.lower() for word in response.xpath("//img/@alt").getall() if word
        ] + [word.lower() for word in response.xpath("//img/@src").getall() if word]
        return list(
            set(
                pay
                for scrapped_src in res_payment
                for pay in payments_keywords
                if pay in scrapped_src
            )
        )

    def extract_b2b_keywords(self, response: scrapy.http.response) -> List:
        """
        extract bb2 keywords pre-defined under settings.py from html body

        Returns: a list of b2b keywords if they are presented
        """
        item = GeneralInformationItem()
        b2b_keywords = self.settings["B2B_KEYWORDS"]

        try:
            data = response.body.decode("utf-8").lower()
        except UnicodeDecodeError:
            data = response.body.decode("ISO-8859-1").lower()

        b2b_key_dict = {}
        for word in b2b_keywords:
            if re.search(word, data) is not None:
                b2b_key_dict[word] = True
            else:
                b2b_key_dict[word] = False
        if any(value is True for value in b2b_key_dict.values()):
            item["tagged_as_b2b"] = True
        else:
            item["tagged_as_b2b"] = False

        return [k for k, v in b2b_key_dict.items() if v]

    def extract_webshop_system(self, response: scrapy.http.response) -> List:
        """
        extract webshop keywords pre-defined under settings.py from html body

        Returns: a list of webshop system keywords if they are presented
        """
        webshop_sys = []
        websystem_keywords = self.settings["WEBSYSTEMS_KEYWORDS"]
        websystem_keywords = [i.lower() for i in websystem_keywords]
        try:
            data = response.body.decode("utf-8").lower()
        except UnicodeDecodeError:
            data = response.body.decode("ISO-8859-1").lower()
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

        for link in LinkExtractor().extract_links(response):
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

    def extract_price_info(self, response: scrapy.http.response, company_url) -> Dict:
        """
        extract price information by matching any numeric up to 10 digits before and after
        decimal indicator comma or dot for currency € and $

        Returns: A dict with keys of products_avg_price and products_quantity
        """

        self.logger.info("start extracting price...")
        try:
            data = response.body.decode("utf-8").lower()
        except UnicodeDecodeError:
            data = response.body.decode("ISO-8859-1").lower()

        currency_sign = self.settings["CURRENCY_SIGN"]
        price_pattern = self.settings["PRICE_PATTERN"]

        if not re.search(currency_sign, data).group():
            return None

        currency = re.search(currency_sign, data).group()
        price_lst = re.findall(price_pattern, data)
        price_lst = [float(p.strip().replace(",", ".")) for p in price_lst]
        yield PriceItem(
            **{
                "products_avg_price": round(sum(price_lst) / len(price_lst), 2)
                if price_lst
                else None,
                "products_quantity": len(price_lst),
                "currency": currency,
                "company_url": company_url,
            }
        )


def create_report_dataset(
    wappalyzer_data_column: str = "wappalyzer",
):
    """
    create final report for scrapped results
    1. assume we will always have wappalyzer data in the column as this is the part of the pipeline.
    this part of data is normalized and then converted from a pandas series of dict into columns
    2. the report is saved under default result folder with the surffix __report

    Returns: None
    """
    general_info_path = settings["FILE_FOLDE"] / "generalinformationitem.csv"
    price_info_path = settings["FILE_FOLDE"] / "priceitem.csv"

    general_info_df = pd.read_csv(general_info_path)
    logging.info(
        "scraped general information dataframe is of %s", general_info_df.shape
    )

    price_df = pd.read_csv(price_info_path)
    logging.info("scraped price information dataframe is of %s", price_df.shape)

    price_df = (
        price_df.groupby("company_url")
        .agg(
            {
                "products_avg_price": "mean",
                "currency": "first",
                "products_quantity": "sum",
            }
        )
        .rename(columns={"products_quantity": "total_num_products"})
    )

    wappalyzer_df = normalize_wappalyzer_data(general_info_df[wappalyzer_data_column])
    general_info_df.drop(wappalyzer_data_column, inplace=True, axis=1)
    update_df = pd.concat([general_info_df, wappalyzer_df], axis=1).set_index(
        "company_url"
    )

    report_df = update_df.join(price_df, on="company_url")

    save_file_path = settings["FILE_FOLDE"] / f"{LeadSpider.name}__report.csv"

    report_df.to_csv(save_file_path)
    logging.info("final report dataframe is of %s", report_df.shape)
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
