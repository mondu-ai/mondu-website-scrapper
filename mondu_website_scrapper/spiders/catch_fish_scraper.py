""" Define scraper spider"""

import logging
import re
import time
from typing import Any, Optional

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.project import get_project_settings
from Wappalyzer import Wappalyzer, WebPage

from mondu_website_scrapper.gsheet_api.read_from_gsheet import read_from_gsheet
from mondu_website_scrapper.items import ContactItem, GeneralInformationItem, PriceItem
from mondu_website_scrapper.report import CreateReportDataSet

settings = get_project_settings()
wappalyzer = Wappalyzer.latest()

# pylint: disable=R0201


class LeadSpider(scrapy.Spider):
    """
    our first spider for crawling web pages.

    Returns: the direct returns are items that in python dictionary format.
    It will be later passed to pipelines.

    Yields: yeild an item and item pipeline will export it as a csv file
    """

    name = "findingnemo"

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
    }

    def _get_start_urls(self):

        if self.use_gsheet:
            # self.settings["INPUT_URL_COLUMN_NAME"] is not None:
            input_column = self.settings["INPUT_URL_COLUMN_NAME"]

            return (
                read_from_gsheet(input_columns=[input_column])[input_column]
                .unique()
                .tolist()
            )
        else:
            return self.settings["START_URLS"]

    def __init__(self, use_gsheet: bool, *args, **kwargs):
        super(LeadSpider, self).__init__(*args, **kwargs)
        self.settings = settings

        self.external_urls = kwargs.get("external_urls", None)
        self.use_gsheet = use_gsheet
        if self.external_urls is not None:

            self.start_urls = self.external_urls
        else:
            self.start_urls = self._get_start_urls()

    def parse(self, response) -> scrapy.Item:  # pylint: disable=arguments-differ
        """
        the parse method inherited from scrapy.Spider. overwrite it with our own returns.

        Yields: item, in a python dict format, containes scraped information.
        """
        item = GeneralInformationItem()
        item["company_url"] = response.url
        item["status"] = response.status
        languages = response.css("html").xpath("@lang")
        for lang in languages:
            item["languages"] = lang.get()

        item["webshop_urls"] = self.extract_webshop_url(response)
        item["payments"] = self.extract_payments(response)
        item["webshop_system"] = self.extract_webshop_system(response)
        item["tagged_by_b2b_words"] = self.extract_b2b_keywords(response)
        item["wappalyzer"] = self.extract_wappalyzer_data(response)

        # get information for product
        link_prod_extractor = LinkExtractor(
            allow=f"{response.url}.*(collection|product|produkte|kategories|categories)",
            unique=True,
        )

        for link in link_prod_extractor.extract_links(response):
            self.logger.info("sending request to product page...")
            yield scrapy.Request(
                link.url,
                callback=self.extract_price_info,
                cb_kwargs={"company_url": response.url},
                dont_filter=True,
            )

        # get information for contact information

        link_contact_extractor = LinkExtractor(
            allow=f"{response.url}.*(impressum|kontakt)",
            unique=True,
        )

        for link in link_contact_extractor.extract_links(response):
            self.logger.info("sending request to contact information page...")
            yield scrapy.Request(
                link.url,
                callback=self.extract_contact_information,
                cb_kwargs={"company_url": response.url},
                dont_filter=True,
            )

        # get information for social media
        link_social_media_extractor = LinkExtractor(
            allow="linkedin|facebook|youtube|twitter|instagram|xing", unique=True
        )
        social_media_lst = []

        for link in link_social_media_extractor.extract_links(response):
            self.logger.info("looking for social media hyperlinks...")
            social_media_lst.append(link.url)
        item["social_media"] = social_media_lst

        yield item

    def extract_webshop_url(self, response: scrapy.http.response) -> list:
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

    def extract_payments(self, response: scrapy.http.response) -> list:
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

    def extract_b2b_keywords(self, response: scrapy.http.response) -> list:
        """
        extract bb2 keywords pre-defined under settings.py from html body

        Returns: a list of b2b keywords if they are presented
        """
        b2b_keywords = self.settings["B2B_KEYWORDS"]

        try:
            data = response.body.decode("utf-8").lower()
        except UnicodeDecodeError:
            data = response.body.decode("ISO-8859-1").lower()

        b2b_key_lst = []
        for word in b2b_keywords:
            b2b_key_lst += [word] if re.search(word, data) is not None else []
        return b2b_key_lst

    def extract_webshop_system(self, response: scrapy.http.response) -> list:
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
    ) -> dict[str, dict[str, Any]]:
        """
        using wappalyzer api extract info

        returns: dict
        """
        webpage = WebPage.new_from_url(response.url)
        return wappalyzer.analyze_with_categories(webpage)

    def extract_price_info(
        self, response: scrapy.http.response, company_url: str
    ) -> scrapy.Item:
        """
        extract price information by matching any numeric up to 10 digits before and after
        decimal indicator comma or dot for currency € and $

        Returns: A dict with keys of products_avg_price and products_quantity
        """

        # self.logger.info("start extracting price...")
        try:
            data = response.body.decode("utf-8").lower()
        except UnicodeDecodeError:
            data = response.body.decode("ISO-8859-1").lower()

        currency_sign = self.settings["CURRENCY_SIGN"]
        price_pattern = self.settings["PRICE_PATTERN"]

        if not re.search(currency_sign, data).group():
            yield None

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

    def extract_contact_information(
        self, response: scrapy.http.response, company_url: str
    ) -> scrapy.Item:
        """
        extract phone and email address from imprint and contact page
        the way to extract those information is quite fuzzy.
        I am brutally searching within imprint and contact page anything digits starting from
        +43 and +49 for AU and DE market respectively.

        Returns: A ContactItem
        """
        try:
            data = response.body.decode("utf-8").lower()
        except UnicodeDecodeError:
            data = response.body.decode("ISO-8859-1").lower()
        phone_pattern = self.settings["PHONE_PATTERN"]
        email_pattern = self.settings["EMAIL_PATTERN"]
        phone = re.findall(phone_pattern, data)
        email = re.findall(email_pattern, data)
        yield ContactItem(
            **{
                "company_url": company_url,
                "contact_information_url": response.url,
                "phone": list(set(phone)),
                "email": list(set(email)),
            }
        )


def main(
    use_cache: bool = True,
    use_gsheet: bool = True,
    external_scrape_urls: Optional[list[str]] = None,
) -> None:
    """
    this is the main function for calling scraper and generating report
    if use_cache, scraper will skip the scraping process and create report directly by using
    existing csv files under scraped_results folder, otherwise, scraper start from scratch.
    if use_gsheet, scraper will read given urls from pre-defined gsheet, otherwise, scraper will
    read urls from settings.py.

    return: Create a report findingnemo__report.csv under scraped_results folder.
    """
    if not use_cache:
        process = CrawlerProcess(settings)

        process.crawl(
            LeadSpider, use_gsheet=use_gsheet, external_urls=external_scrape_urls
        )
        start_time = time.time()
        process.start()
        logging.info("--- %s seconds ---", (time.time() - start_time))

    report = CreateReportDataSet()
    report.join_all_scraped_items()


if __name__ == "__main__":
    import argparse

    # Initiate the parser
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--use-cache",
        type=bool,
        help="decide if use cached data",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--use-gsheet",
        type=bool,
        help="decide if use gsheet as urls input",
        action=argparse.BooleanOptionalAction,
    )
    parser.add_argument(
        "--external-scrape-urls",
        help="pass urls for scraping",
        nargs="+",
        type=str,
    )
    # Read arguments from the command line
    args = parser.parse_args()
    main(args.use_cache, args.use_gsheet, args.external_scrape_urls)
